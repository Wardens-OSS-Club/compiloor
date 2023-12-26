from datetime import datetime

from json import dumps, loads

from os import listdir
from os.path import abspath

from typing import Tuple

from requests import get

from compiloor.constants.utils import REPORT_EXTENSION
from compiloor.constants.environment import (
    CONFIG_DIRECTORY, FINDINGS_DIRECTORY, REPORTS_DIRECTORY, MAIN_DIRECTORY
)
from compiloor.services.typings.config import ProtocolInformationConfigDict
from compiloor.services.typings.finding import Severity


class FileUtils:
    """
        Utility class for file operations.
    """
    
    @staticmethod
    def read_config(json: bool = False) -> str | ProtocolInformationConfigDict:
        """
            Returns the serialized contents of the config file.
        """
        
        _config = open(abspath(CONFIG_DIRECTORY), "r").read()
        
        _config = loads(_config) 
        
        for file in listdir(abspath(MAIN_DIRECTORY+ "/sections")):
            if not file.endswith(".md"): continue
            
            _config[file.replace(".md", "")] = open(abspath(MAIN_DIRECTORY + f"/sections/{file}"), "r").read()
        
        if not json and isinstance(_config, dict): _config = dumps(_config, indent=4)
        
        return _config
    
    @staticmethod
    def read_finding(severity: Severity, index: int) -> str:
        """
            Returns the contents of the finding with the given severity and index.
        """
        
        return open(abspath(FINDINGS_DIRECTORY) + f"/[{severity.cast_to_folder_sig().value}-{FileUtils.get_fs_sig_index(index)}].md", "r").read()
    
    @staticmethod
    def read_file(name: str, is_url: bool = False, html_tag: str | None = None) -> str:
        """
            Returns the contents of the file with the given name. Wrapps them in the given HTML tag if provided.
        """

        file: str = open(abspath(name), "r").read() if not is_url else get(name).content.decode("utf-8")
        
        if html_tag: file = f"<{html_tag}>{file}</{html_tag}>"
        
        return file
    
    @staticmethod
    def get_fs_sig_index(index: int) -> str:
        """
            Returns the report index in the proper signature format.
        """
        
        return "0" + str(index) if index < 10 else str(index)

    @staticmethod
    def get_current_timestamp() -> str:
        """
            Returns the current timestamp in the proper signature format.
        """
        
        return datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    
    @staticmethod
    def get_timestamp_fs_sig_index() -> int:
        """
            Returns the current timestamp in the proper signature format.
        """
        _timestamp = FileUtils.get_current_timestamp()
        return FileUtils.get_fs_sig_index(
            len([occurence for occurence in listdir() if _timestamp in occurence])
        )

class FindingUtils:
    """
        Utility class for findings.
    """
    
    @staticmethod
    def get_current_finding_amount(severity: Severity) -> int:
        """ 
            Returns the current amount of findings for the given severity.
        """
        return len(
            list(
                filter(
                    lambda x: x.endswith(".md") and x.startswith(f"[{severity.cast_to_folder_sig().value}"), listdir(abspath(FINDINGS_DIRECTORY))
                )
            )
        )
    
    @staticmethod
    def get_finding_fragments() -> Tuple[int, dict[Severity, int], dict[Severity, list[str]]]:
        
        """
            Returns a tuple of two dictionaries:
            - The first one contains the amount of findings per severity.
            - The second one contains the findings themselves.
        """
        
        total_findings: int = 0
        
        findings_by_severity_amount: dict[Severity, int] = {}
        findings_by_severity: dict[Severity, str] = {}
        
        for _severity in Severity:
            findings_amount_by_severity = FindingUtils.get_current_finding_amount(_severity)
            findings_by_severity_amount[_severity] = findings_amount_by_severity
            total_findings += findings_amount_by_severity
            findings_by_severity[_severity] = [
                FileUtils.read_finding(_severity, finding) for finding in range(1, findings_amount_by_severity + 1)
            ] 
            
        return [
            total_findings, findings_by_severity_amount, findings_by_severity
        ]       
    
class ReportUtils:
    """
        Class with utility functions for report generation.
    """
    
    @staticmethod
    def get_current_report_count() -> int:
        """
            Returns the current report count.
        """
        
        return len(listdir(abspath(REPORTS_DIRECTORY)))
    
    @staticmethod
    def get_report_name(index: int | None) -> str:
        """
            Returns the name of the report with the given index.
        """
        
        if not index: index = ReportUtils.get_current_report_count()
        return f'{abspath(REPORTS_DIRECTORY)}/report-{FileUtils.get_fs_sig_index(index)}{REPORT_EXTENSION}'