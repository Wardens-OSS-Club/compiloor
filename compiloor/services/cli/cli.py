from typer import Typer

from typing_extensions import Annotated

from compiloor.services.environment.utils import FileUtils
from compiloor.services.logger import Logger
from compiloor.services.parser.chromium import create_chromium_document
from compiloor.services.parser.indexing import create_report_with_page_numbers_and_legend
from compiloor.services.parser.utils import ReportCustomizer
from compiloor.services.typings.finding import SeverityAnnotation
from compiloor.services.environment import (
    current_directory_initialized, findings_directory_not_empty, initialize_directory,
    add_finding_template
)
from compiloor.constants.environment import INITIALIZED, NOT_INITIALIZED
from compiloor.services.utils.config import ConfigUtils

cli = Typer()

@cli.command("init")
def init(force: Annotated[bool, "force"] = False):
    current_directory_initialized(NOT_INITIALIZED, force)
    initialize_directory(force)
    
@cli.command("add-finding")
def add_finding(severity: Annotated[SeverityAnnotation, "severity"] = SeverityAnnotation.MEDIUM.value):
    current_directory_initialized(INITIALIZED)
    add_finding_template(severity.cast_to_severity())

@cli.command("compile")
def compile_report():
    current_directory_initialized(INITIALIZED)
    findings_directory_not_empty()
    ConfigUtils.validate_config_template_urls(FileUtils.read_config(json=True))
    
    # The customizer creates the base report and handles almost all serialization:
    customizer = ReportCustomizer()
    
    # Save the initial report to a PDF file:
    report_path = create_chromium_document(customizer.report)
    
    # Finalize the report by adding page numbers and a legend:
    create_report_with_page_numbers_and_legend(report_path, customizer.report_section_headings)
    Logger.success(f"Successfully compiled the report to {report_path}!")

