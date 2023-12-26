from json import dumps

from os import listdir, mkdir
from os.path import abspath, isdir, isfile, join

from shutil import rmtree

from compiloor.constants.environment import (
    BASE_CONFIG_SCHEMA, BASE_FINDING_MD_TEMPLATE, CONFIG_NAME,
    FINDINGS_DIRECTORY, MAIN_DIRECTORY, REPORTS_DIRECTORY
)
from compiloor.constants.logger import ALREADY_INITIALIZED_MSG, NOT_INITIALIZED_MSG
from compiloor.services.environment.utils import FileUtils, FindingUtils
from compiloor.services.typings.finding import Severity
from compiloor.services.logger import Logger
from compiloor.services.utils.config import ConfigUtils


# TODO: Rewrite the following functions into a utility class:
def current_directory_initialized(initialized: bool = True, force: bool = False) -> None:
    if force or _current_directory_initialized() == initialized: return
    Logger.error(ALREADY_INITIALIZED_MSG if initialized else NOT_INITIALIZED_MSG)
    exit(1)

def _current_directory_initialized() -> bool:
    return isdir(abspath(MAIN_DIRECTORY)) and isdir(abspath(FINDINGS_DIRECTORY))

def initialize_directory(force: bool = False) -> None:
    # erase everything if force:
    
    _abs_main_dir = abspath(MAIN_DIRECTORY)
    _abs_findings_dir = abspath(FINDINGS_DIRECTORY)
    
    if force: rmtree(_abs_main_dir, ignore_errors=True)

    try:
        if not isdir(_abs_findings_dir): mkdir(_abs_findings_dir)

        mkdir(_abs_main_dir)
        mkdir(abspath(REPORTS_DIRECTORY))
        mkdir(join(_abs_main_dir, "sections"))

        config: str

        if not isfile(ConfigUtils.get_base_config_location()):
            config = dumps(BASE_CONFIG_SCHEMA, indent=4)
            ConfigUtils.mutate_base_config(config, False)
        else:
            config = open(ConfigUtils.get_base_config_location()).read()
            
        open(join(_abs_main_dir, CONFIG_NAME), "w").write(config)

        for key in ["about_author_content", "disclaimer_content", "introduction_content", "about_protocol_content", "security_assessment_summary_content"]:
            open(join(_abs_main_dir, "sections", f"{key}.md"), "w").write("write markdown here")

        Logger.success("Successfully initialized the directory!")
        
    except Exception as err:
        Logger.error(f"An error occured while initializing the directory: {err}")
        exit(1)

def add_finding_template(severity: Severity) -> None:
    """
        Adds a finding template to the findings directory.
    """
    
    try:
        finding_template = BASE_FINDING_MD_TEMPLATE

        folder_sig = severity.cast_to_folder_sig().value
        
        index = FileUtils.get_fs_sig_index(FindingUtils.get_current_finding_amount(severity) + 1)

        # setting the index and severity:
        finding_template = finding_template.replace("{{finding_severity}}", folder_sig)
        finding_template = finding_template.replace("{{finding_index}}", index)    
        
        open(join(abspath(FINDINGS_DIRECTORY), f"[{folder_sig}-{index}].md"), "w").write(finding_template)
        
        Logger.success(f'Successfully added a finding template for severity "{severity.name}"!')
    except Exception as err:
        Logger.error(f"An error occured while adding a finding template: {err}")
        exit(1)
        
@staticmethod
def findings_directory_not_empty() -> None:
    """
        Raises an exception if the findings directory is empty.
    """
    dir: list[str] = listdir(abspath(FINDINGS_DIRECTORY))
    if '.DS_Store' in dir: dir.remove('.DS_Store')

    if dir: return
    Logger.error("The findings directory is empty!")
    exit(1)