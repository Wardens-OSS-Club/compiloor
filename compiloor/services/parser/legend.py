from compiloor.services.parser.finding import Finding
from compiloor.services.typings.finding import Severity


def create_finding_severities_legend_html(findings_section_index: str, findings: list[Finding]) -> tuple[str, dict[Severity, int]]:
    """
        Creates an HTML fragment with the findings severities legend. \n
        :note: The page numbers of the seperate findings get added in a later stage of the report generation process.
    """
    
    # The bellow code can only work with strings so we are casting the findings_section_index to a string here:
    if not isinstance(findings_section_index, str):
        findings_section_index = str(findings_section_index) 
    
    # Keeping all of the finding-related indexes together and then simply joining them. 
    # TODO: This should be re-done after the class modularization process is complete.
    fragments = []
    
    current_severity, current_severity_index, current_severity_finding_index = None, 0, 0

    severity_to_index: dict[Severity, int] = {}

    for finding in findings:
        if finding.severity != current_severity:
            # Tracking the current severity in order to know when to add another subsection:
            current_severity = finding.severity
            
            current_severity_index += 1 # The severity's index in the legend.
            current_severity_finding_index = 0 # The finding's index in the legend.
            
            # The severities are indexed with sub-section indexes (i.e. 8.1) and the findings are indexed with their own identifiers: i.e. [H-01], etc.:
            section_index = f'[{findings_section_index}.{current_severity_index}]_page'

            severity_to_index[finding.severity] = current_severity_index

            if current_severity_index != 1: fragments.append("<div>")

            # TODO: Can we isolate the html fragments in some seperate place?
            # TODO: Make the style system more modular.
            fragments.append(
                # The severity's legend entry in html:
                f'''
                    <div class="sub-paragraph">
                        <a href="#section-{findings_section_index}-{current_severity_index}">
                            <div class="section-wrapper">
                                <p>
                                    {findings_section_index}.{current_severity_index}. {current_severity.cast_to_display_case()} Findings
                                </p>
                                {{{{{section_index}}}}}
                            </div>
                        </a>
                    </div>
                '''
            )

        current_severity_finding_index += 1
        section_index = f'[{finding.id}]_page'

        # TODO: Can we isolate the html fragments in some seperate place?
        # TODO: Make the style system more modular.
        fragments.append(
            # The finding's legend entry in html:
            f'''
            <div class="sub-sub-paragraph">
                <a href="#section-{findings_section_index}-{current_severity_index}-{current_severity_finding_index}">
                    <div class="section-wrapper">
                        <p class="legend-section-heading">[{finding.id}] {finding.title.replace("`", "")}</p>
                        <p class="page-number">{{{{{section_index}}}}}</p>
                    </div>
                </a>
            </div>
            '''
        )

    return ("".join(fragments), severity_to_index)