from os.path import abspath


FINDING_TEMPLATE_NAME: str = "finding-template.md"
CONFIG_NAME: str = "config.json"

INITIALIZED: bool = True
NOT_INITIALIZED: bool = False

MAIN_DIRECTORY: str = "compiloor-report"
MAIN_DIRECTORY_ABS_PATH: str = abspath(MAIN_DIRECTORY)

FINDINGS_DIRECTORY: str = "findings"
REPORTS_DIRECTORY: str = MAIN_DIRECTORY + "/reports"
TEMPLATE_DIRECTORY: str = "templates"

CONFIG_DIRECTORY: str = MAIN_DIRECTORY + "/" + CONFIG_NAME

FINDING_LIST_TABLE_COLUMNS = ["ID", "Title", "Severity", "Status"]

BASE_CONFIG_SCHEMA: dict[str, str] = {
    "title": "SECURITY RESEARCHER NAME",
    "author": "-",
    "date": "-",
    "company_name": "COMPANY NAME",
    "protocol_name": "PROTOCOL NAME",
    "repository": "-",
    "type": "-",
    "commit": "-",
    "sloc": "-",
    # Sections of the report. They go trough an md renderer.
    "about_author_content": "ABOUT SECTION",
    "disclaimer_content": "DISCLAIMER CONTENT",
    "introduction_content": "INTRODUCTION CONTENT",
    "about_protocol_content": "ABOUT PROTOCOL CONTENT",
    "security_assessment_summary_content": "SECURITY ASSESSMENT SUMMARY CONTENT",
    # Should be valid URLs.
    "template_url": "REPORT URL",
    "stylesheet_url": "REPORT CONTENT",
    "cover_img_url": "COVER IMAGE URL",
}

FINDING_RESOLUTION_STATUS_HEADING: str = "## _STATUS_="

FINDING_RESOLUTION_STATUS_SECTION: str = FINDING_RESOLUTION_STATUS_HEADING + "{{resolution_status}}"

# Example:
"""
# [M-00]

## Severity

**Impact:**

**Likelihood:**

## Description

## Recommendations

## _STATUS_={{resolution_status}}
"""
BASE_FINDING_MD_TEMPLATE: str = f"""# [{{{{finding_severity}}}}-{{{{finding_index}}}}]

## Severity

**Impact:**

**Likelihood:**

## Description

## Recommendations

{FINDING_RESOLUTION_STATUS_SECTION}
""" 