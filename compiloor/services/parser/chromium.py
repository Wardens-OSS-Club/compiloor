from bs4 import BeautifulSoup

from os.path import abspath

from playwright.sync_api import sync_playwright

from compiloor.services.environment.utils import FileUtils, ReportUtils
from compiloor.constants.environment import REPORTS_DIRECTORY
from compiloor.constants.utils import REPORT_EXTENSION


def create_chromium_document(fragment: str, dir: str = abspath(REPORTS_DIRECTORY)) -> str:
    """
        Creates a PDF document from the given HTML fragment and saves it in the given directory.
    """
    
    # This cleans empty tags added by the parser:
    for tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul"]: fragment = fragment.replace(f"<{tag}></{tag}>", "")
    fragment = BeautifulSoup(fragment, "html.parser")

    # Using a context manager just because the documentation says so:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        document = browser.new_page()
        document.set_content(str(fragment), wait_until="networkidle") # Wait until the page is fully loaded.
        report_index = ReportUtils.get_current_report_count() + 1 # Adding 1 for the new index
        
        dir = f'{dir}/report-{FileUtils.get_fs_sig_index(report_index)}{REPORT_EXTENSION}'
        document.emulate_media(media="screen")
        document.pdf(path=dir, print_background=True, prefer_css_page_size=True, format="A4")
        # Keeping the html digest for debugging purposes:
        open("report.html", "w").write(document.content())
        
        browser.close()
    return dir