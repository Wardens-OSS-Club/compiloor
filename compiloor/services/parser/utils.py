from inspect import getmembers, ismethod

from compiloor.constants.report import (
    INFORMATION_TABLE_VARIABLES,
    REPORT_SECTION_HEADINGS,
    RISK_CLASSIFICATION_MAIN_CONTENT_MD,
    RISK_CLASSIFICATION_IMPACT_CONTENT_MD,
    RISK_CLASSIFICATION_LIKELIHOOD_CONTENT_MD,
    RISK_CLASSIFICATION_ACTION_REQUIRED_CONTENT_MD
)
from compiloor.constants.utils import MAIN_REPORT_SECTIONS
from compiloor.services.environment.utils import FileUtils, FindingUtils
from compiloor.services.parser.finding import Finding
from compiloor.services.parser.legend import create_finding_severities_legend_html
from compiloor.services.parser.markdown import create_html_from_markdown
from compiloor.services.parser.table import TableUtils
from compiloor.services.typings.config import ProtocolInformationConfigDict
from compiloor.services.typings.finding import Severity

class ReportCustomizer:
    """
        A class that assembles the core report. 
    """
    
    # Report configuration variables:
    config: ProtocolInformationConfigDict
    
    # Report template variables:
    report: str # The report template.
    stylesheet: str # The CSS stylesheet.
    
    # Finding report variables:
    total_findings_amount: int # The total amount of findings.
    finding_amounts_by_severity: dict[Severity, int] # The amount of findings per each severity.
    findings: str # The finding fragments in HTML format.
    serialized_findings: list[Finding] # The serialized findings in Finding object format.
    report_section_headings: list[str] # The report section headings.
    severity_to_index: dict[Severity, int] # The severity to index mapping.
    
    def __init__(self, markdown: bool) -> str:
        # Gets the report configuration:
        self.config = FileUtils.read_config(json=True)
        self.config["render_markdown"] = markdown

        # Gets the stylesheet and report template fragment:         
        self.report = FileUtils.read_file(self.config["template_url"], is_url=True)
        self.stylesheet = FileUtils.read_file(self.config["stylesheet_url"], is_url=True, html_tag="style")
        
        # Gets the finding fragments:
        self.fetch_finding_fragments(self.config, 8) # 8 is the hardcoded index of the findings section: Will be changed in a future update.
        
        self.assemble_report() # Assembles the report.
    
    def add_report_config_variables(self) -> None:
        for key in self.config.keys():
            _value = str(self.config[key])
            
            # Signifies that the value is a markdown fragment:
            # Parsing such content variables so that they can use markdown syntax:
            if "_content" in key: _value = create_html_from_markdown(_value)
            
            # '{{config.<key>}}' syntax is very confusing when:
            self.report = self.report.replace(f"{{{{config.{key}}}}}", _value)

    def add_information_table_variables_to_report(self, tag: str = "b") -> None:
        """
            Bolds the information table row headings in the report.
        """
        
        for _key in INFORMATION_TABLE_VARIABLES.keys():
            self.report = self.report.replace(
                _key,
                f'<{tag}>{INFORMATION_TABLE_VARIABLES[_key]}</{tag}>'
            )

    def add_dynamic_tables_to_report(self) -> None:
        # Defines the table type -> callable arguments mapping:
        # TODO: This needs to be converted into some modular system trough the config.
        kwargs: dict[str, list[any]] = {
            "severity_classification_table": [],
            "information_table": [self.config],
            "findings_count_table": [self.finding_amounts_by_severity, self.total_findings_amount],
            "findings_summary_table": [self.serialized_findings, self.severity_to_index],
        }
        
        # Maps the table type -> table creation callable:
        table_types = TableUtils.fragment_to_callable()
        
        # Adding the tables to the report:
        for name in table_types.keys():
            callable, args = table_types[name], kwargs[name]
            self.report = self.report.replace(f'{{{{{name}}}}}', callable(*args))
        
        # Adding no-wrap so that the table look doesn't break:
        # TODO: Change with a modular CSS stylesheet.
        self.report = self.report.replace("<td>[", '<td class="no-wrap-column">[')
        
    def add_findings_legend(self) -> None:
        # Adding the legend manually:
        # TODO: Change with a modular system trough the config.
        (findings, self.severity_to_index) = create_finding_severities_legend_html(8, self.serialized_findings)
        self.report = self.report.replace(
            '{{findings_legend}}',
            # 8 is the hardcoded index of the findings section. TODO: Change to a modular section system
            findings
        )
        
    def assemble_report(self) -> None:
        # Adds the main parts of the report to the fragment:
        # i.e. The stylesheet, the findings, the total findings amount.
                
        section_to_attribute: dict[str, any] = {}
        for section in MAIN_REPORT_SECTIONS:
            section_to_attribute[str(section)] = getattr(self, section)
        
        # Adding the section markdowns to the report:
        # f"{{{{{part}}}}}" looks like that due to the f string syntax.
        # It equates to '{{<part>}}' in the report template.
        for part in section_to_attribute.keys():
            self.report = self.report.replace(f"{{{{{part}}}}}", str(section_to_attribute[part]))
        
        # Getting all of the class's methods and calling all with the 'get_' prefix:
        for method in getmembers(self, predicate=lambda x: ismethod(x)):

            # the "add_" is a prefix for all methods in the class
            # that add something in place of a placeholder in the report:
            if not method[0].startswith("add_") or method[0] == "add_dynamic_tables_to_report": continue
            # Calling the method:
            method[1]()
        
        # Even though this is an add method it needs to be called last because 
        # it needs the other report placeholders to already be populated:
        self.add_findings_legend()
        # Calling it here because it needs the severity_to_index mapping:
        self.add_dynamic_tables_to_report()
        
        if self.config["render_markdown"]:
            md_report: str = ""
            
            heading_to_content: dict[str, str] = {
                "Introduction": self.config["introduction_content"],
                "Disclaimer": self.config["disclaimer_content"],
                "About": self.config["about_author_content"],
                f"About {self.config['protocol_name']}" : self.config["about_protocol_content"],
                "Risk Classification": RISK_CLASSIFICATION_MAIN_CONTENT_MD,
                "Impact": RISK_CLASSIFICATION_IMPACT_CONTENT_MD,
                "Likelihood": RISK_CLASSIFICATION_LIKELIHOOD_CONTENT_MD,
                "Action required for severity levels": RISK_CLASSIFICATION_ACTION_REQUIRED_CONTENT_MD,
                "Security Assessment Summary": self.config["security_assessment_summary_content"],
                "Findings": "\n".join([finding.fragment for finding in self.serialized_findings])
            }
                        
            for heading in self.report_section_headings:                
                # Removing double spaces:
                heading = heading.strip().replace(" " * 2, " ")
                
                # Getting the heading's index | Supposed to be in the following format: X.Y.Z.
                md_heading: str = (heading.split(" ")[0].count(".")) * "#"
                
                if self.report_section_headings.index(heading) != 0: md_heading = "\n" + md_heading

                # Removing the heading index from the heading and crafting it back:
                heading = " ".join(heading.split(" ")[1:]).split("</h2>")[0]
                
                if heading == "Executive Summary": continue
                md_report += f"{md_heading} {heading}\n {heading_to_content[heading]}"
                if heading == "Findings": break

                
            self.config["markdown_report"] = md_report
            
            
    def fetch_finding_fragments(
        self,
        config: ProtocolInformationConfigDict,
        findings_section_index: str,
        paragraph_subheading_tag: str = "h2"
    ) -> None:
        """
            Extracts the findings from the ./findings directory and
            serializes them into multiple different formats used arcoss the report generation process.
        """
        
        # Getting multiple different formats of the findings:
        total_amount, amounts_by_severity, findings = FindingUtils.get_finding_fragments()

        # Using this as a copy array with removed empty severity levels:
        # Remove empty severity levels
        _findings = {}

        for severity, fragments in findings.items():
            # Not adding the severity to the report level if it's empty:
            if not fragments: continue
            
            _findings[severity] = fragments

        # Copy the non-empty severity levels
        findings = _findings

        markdowns, _finding_fragments = [], []

        # Copying the static headings present in the report template:
        section_headings = REPORT_SECTION_HEADINGS.copy()

        # Sort severity levels from high to low
        for severity in reversed(list(findings.keys())):
            _finding_fragments.extend(findings[severity])

        serialized = [Finding(finding) for finding in _finding_fragments] # Serializing the findings into the Finding format.

        full_by_severity = {}
        current_severity, severity_index = None, 0

        # Iterate through severity levels from high to low
        for severity in reversed(list(Severity)):
            if not severity in findings: continue # Skip empty severity levels
            
            # Sort findings by severity level
            full_by_severity[severity] = [finding.render_fragment for finding in serialized if finding.severity == severity]

        # Adding the `render_fragment` of each finding to the report:
        for finding in serialized:
            severity_display = finding.severity.cast_to_display_case()
            # Adding the finding's title to the section headings for the sake of indexing it later:
            # example: "[H-01] Finding title"
            # TODO: Can this be done in a more elegant way?
            section_headings.append(f"[{finding.id}] {finding.title}")

            # Skip if the severity level is the same as the previous one
            if finding.severity == current_severity: continue 

            severity_index += 1
            current_severity = finding.severity

            # Adding the severity level heading to the section headings:
            section_headings.append(f"{findings_section_index}.{severity_index}. {severity_display} Findings")

            # Get the HTML fragments in the correct order for the current severity:
            html_fragments = "\n".join(full_by_severity[finding.severity])
            
            # TODO: Can this be done in a more elegant way?
            markdowns.append(
                f'''
                    <div id="section-{findings_section_index}-{severity_index}" class="page-break-after">
                        <{paragraph_subheading_tag} class="paragraph-subheading">
                            {findings_section_index}.{severity_index}. {severity_display} Findings
                        </{paragraph_subheading_tag}>
                        <div>
                            {html_fragments}
                        </div>
                    </div>
                '''
            )

            # Adding the link to the heading:
            markdowns[-1] = markdowns[-1].replace(f'[[{finding.severity.value}_severity_index]]', str(severity_index))
    
        # Currently 4. is hardcoded to be the about protocol section.
        section_headings[3] = section_headings[3] + " " + config["protocol_name"]

        self.total_findings_amount = total_amount
        self.finding_amounts_by_severity = amounts_by_severity
        self.findings = "\n".join(markdowns)
        self.serialized_findings = serialized
        self.report_section_headings = section_headings