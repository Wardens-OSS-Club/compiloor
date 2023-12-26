from typing import Callable

from tabulate import tabulate

from compiloor.constants.environment import FINDING_LIST_TABLE_COLUMNS
from compiloor.constants.report import (
    FINDING_COUNT_TABLE_COLUMNS, INFORMATION_TABLE_VARIABLES,
    SEVERITY_CLASSIFICATION_TABLE_COLUMNS, SEVERITY_CLASSIFICATION_TABLE_ROWS
)
from compiloor.services.parser.markdown import create_html_from_markdown
from compiloor.services.typings.config import ProtocolInformationConfigDict
from compiloor.services.typings.finding import Severity
from compiloor.services.parser.finding import Finding


class HTMLTableUtils:
    """
        A class containing utilities for creating HTML tables.
        
        **Disclaimer**: All of the tables use the '[[variable]]' notation for dynamic values instead of '{{variable}}' on purpose.
    """
    
    @staticmethod
    def create_html_table(
        rows: list[list[str]],
        columns: list[str],
        title: str = "",
        highlight_last_row: bool = False, tag: str = "h3",
        remove_underline_from_title: bool = True
    ) -> tuple[str, str]:
        """
        Creates a table from the given rows and columns.
        """
        
        # Tables use the '[[variable]]' notation for dynamic values instead of '{{variable}}' on purpose.
        # TODO: Serialize the variable system in the future.
        
        table: str = f'''
        <div class="table-wrapper">
            [[title]]
            {tabulate(rows, headers=columns, tablefmt="html")}
        </div>
        '''
        
        table_in_md: str = tabulate(rows, headers=columns, tablefmt="github")
        
        no_underline_heading_class = " " + 'class="no-underline-heading"' if remove_underline_from_title else ''
        
        table = table.replace("[[title]]", "" if not title else f"<{tag}{no_underline_heading_class}>{title}</{tag}>")

        if highlight_last_row:
            row = rows[len(rows) - 1]
            table = table.replace(f'<tr><td>{row}', f'<tr class="bold-text"><td>{row}')

        return str(table)

class CustomTables(HTMLTableUtils):
    """
        A class containing utilities for creating custom tables.
    """
    
    # TODO: Make some system of allowing upgradeability and adding custom tables by users:
    
    @staticmethod
    def clean_row(text: str) -> str:
        """
            Cleans a row of the '[[_bold]]' fragment.
        """
        
        return text.replace('_bold', '').replace('[[', '').replace(']]', '')[9:]
    
    @staticmethod
    def create_severity_classification_table(name: str = "") -> str:
        """
            Creates a severity classification table.
        
            | ------------------ | ------------ | -------------- | ----------- |\n
            | Severity           | Impact: High | Impact: Medium | Impact: Low |\n
            | -------------------| ------------ | -------------- | ----------- |\n
            | Likelihood: High   | Critical     | High           | Medium      |\n
            | -------------------| ------------ | -------------- | ----------- |\n
            | Likelihood: Medium | High         | Medium         | Low         |\n
            | -------------------| ------------ | -------------- | ----------- |\n
            | Likelihood: Low    | Medium       | Low            | Low         |\n
            | -------------------| ------------ | -------------- | ----------- |\n
        """
        
        return TableUtils.create_html_table(
            SEVERITY_CLASSIFICATION_TABLE_ROWS,
            SEVERITY_CLASSIFICATION_TABLE_COLUMNS,
            name
        )
        
    
    @staticmethod
    def create_information_table(
        config: ProtocolInformationConfigDict,
        name: str  = "Protocol Summary",
        information_row_heading_tag: str = "b"
    ) -> str:
    
        """
            Creates a protocol information table from the given config.
            
            | -------------- | ----------------------- |\n
            | Protocol Name  | Example Name            |\n
            | -------------- | ----------------------- |\n
            | Repository     | Some repo               |\n
            | -------------- | ----------------------- |\n
            | Date           | September 14th 2023     |\n
            | -------------- | ----------------------- |\n
            | Type           | Lending Protocol        |\n
            | -------------- | ----------------------- |\n
            | SLOC           | 500                     |\n
            | -------------- | ----------------------- |\n

        """
        
        rows: list[list[str]] = []
        
        for row in INFORMATION_TABLE_VARIABLES.keys():
            if config[CustomTables.clean_row(row)] == "-": continue
            rows += [[row, row + "_VALUE"]]
            
        table: str = HTMLTableUtils.create_html_table(
            rows, 
            [], # PROTOCOL_INFORMATION_TABLE_COLUMNS,
            name
        )
                
        for _key in INFORMATION_TABLE_VARIABLES.keys():
            value = create_html_from_markdown(config[CustomTables.clean_row(_key)])
            if value.startswith("<p>"): value = value.replace("<p>", "").replace("</p>", "")
            table = table.replace(_key + "_VALUE", value).replace(
                _key,
                f'<{information_row_heading_tag}>{INFORMATION_TABLE_VARIABLES[_key]}</{information_row_heading_tag}>'
            )
                    
        return table
    
    @staticmethod
    def create_findings_count_table(
        finding_amounts_by_severity: dict[Severity, int],
        total_findings_amount: int,
        name: str = "Findings Count"
    ) -> str:
        """
            Creates a findings count table from the given finding counts.
        
            | -------------- | ----------------------- |\n
            | Severity       | Amount                  |\n
            | -------------- | ----------------------- |\n
            | Critical       | 0                       |\n
            | -------------- | ----------------------- |\n
            | High           | 0                       |\n
            | -------------- | ----------------------- |\n
            | Medium         | 0                       |\n
            | -------------- | ----------------------- |\n
            | Low            | 0                       |\n
            | -------------- | ----------------------- |\n
            | QA             | 0                       |\n
            | -------------- | ----------------------- |\n
            | GAS            | 0                       |\n
            | -------------- | ----------------------- |\n
            | Total Findings | 0                       |\n
            | -------------- | ----------------------- |\n
        """
        
        finding_counts = []
        
        for severity in finding_amounts_by_severity:
            _amount = finding_amounts_by_severity[severity]
            if _amount == 0: continue
            finding_counts.append([severity.cast_to_display_case(), _amount])
        
        # Doesn't allow me to do a one-liner because reverse doesn't return the mutated array,
        # but rather mutates the pointer of the array.
        finding_counts.reverse()

        finding_counts += [["{{total_findings}}", "{{total_findings_amount}}"]]     
            
        table = TableUtils.create_html_table(
            finding_counts,
            FINDING_COUNT_TABLE_COLUMNS,
            name,
            True
        )
        
        return (
            (
                table.replace("{{total_findings}}", f'<b>Total Findings</b>')
            ).replace("{{total_findings_amount}}", f'<b>{total_findings_amount}</b>')
        )    
    
    def create_findings_summary_table(findings: list[Finding], severity_to_index: dict[Severity, int], name: str = "Summary of Findings") -> str:
        """
            Creates a summary of findings table from the given findings.
        
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
            | ID             | Title                   | Severity                | Status       |\n
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
            | [C-01]         | Some finding             | Critical                | Resolved     |\n
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
            | [H-01]         | Some finding             | High                    | Resolved     |\n
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
            | [M-01]         | Some finding             | Medium                  | Resolved     |\n
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
            | [L-01]         | Some finding             | Low                     | Resolved     |\n
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
            | [QA-01]        | Some finding             | QA                      | Resolved     |\n
            | -------------- | ----------------------- | ----------------------- | -------------|\n
            | [GAS-01]       | Some finding             | GAS                     | Resolved     |\n
            | -------------- | ----------------------- | ----------------------- | ------------ |\n
        """
        
        table = TableUtils.create_html_table(
            [TableUtils.finding_to_table_row(finding) for finding in findings],
            FINDING_LIST_TABLE_COLUMNS,
            name
        )
            
        for finding in findings:
            _severity_index: int = severity_to_index[finding.severity]
            table = table.replace(
                f'[{finding.id}]',
                f'<a href="#section-8-{_severity_index}-{finding.id_num}">[{finding.id}]</a>'
            )
            
        return table            
    
class TableUtils(CustomTables):
    """
        A wrapper class for the other table classes in this file.
    """
    
    @staticmethod
    def finding_to_table_row(finding: Finding) -> list[str]:
        """
            Converts a finding to a table row array.
        """
        
        # Example: '[C-01] Some critical finding'
        return [
            f"[{finding.id}]", # Example: [C-01]
            finding.title.replace("`", ""),
            finding.severity.cast_to_display_case(),
            finding.status.value
        ]
    
    @staticmethod
    def tables() -> list[str]:
        """
            Returns a list of the table utilities.
            
            We need this method because if an enum gets created a circular dependency will occur.
        """
        
        # TODO: Convert this into some modular systen with the config.
        return [
            "severity_classification_table",
            "information_table",
            "findings_count_table",
            "findings_summary_table"
        ]
            
    @staticmethod
    def fragment_to_callable() -> dict[str, Callable]:
        """
            Returns a dictionary of the table utilities.
            
            We need this method because if an enum gets created a circular dependency will occur.
        """

        # TODO: Convert this into some modular systen with the config.
        return {
            "severity_classification_table": TableUtils.create_severity_classification_table,
            "information_table": TableUtils.create_information_table,
            "findings_count_table": TableUtils.create_findings_count_table,
            "findings_summary_table": TableUtils.create_findings_summary_table
        }