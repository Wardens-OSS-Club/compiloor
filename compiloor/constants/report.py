REPORT_VARIABLES: list[str] = [
    '[[protocol_name_bold]]',
    '[[protocol_repository_bold]]',
    # '[[protocol_commit_bold]]', 
    '[[protocol_date_bold]]',
    '[[type_bold]]',
    '[[protocol_sloc_bold]]',
]

INFORMATION_TABLE_VARIABLES: dict[str, str] = {
    '[[protocol_protocol_name_bold]]': 'Protocol Name',
    '[[protocol_repository_bold]]': 'Repository',
    # '[[protocol_commit_bold]]': 'Commit', 
    '[[protocol_date_bold]]': 'Date',
    '[[protocol_type_bold]]': 'Protocol Type',
    '[[protocol_sloc_bold]]': 'SLOC'
}

REPORT_SECTION_HEADINGS: list[str] = [
    "1. About", "2. Disclaimer",
    "3. Introduction", "4. About", "5. Risk Classification",
    "5.1. Impact", "5.2. Likelihood",
    "5.3. Action required for severity levels",
    "6. Security Assessment Summary",
    "7. Executive Summary", "8. Findings"
]

PROTOCOL_INFORMATION_TABLE_COLUMNS: list[str] = [
    "Protocol Name",
    # "Repository",
    "Commit", 
    "Date",
    "Protocol Type", 
    "SLOC"
]

SEVERITY_CLASSIFICATION_TABLE_ROWS: list[list[str]] = [
    ["Likelihood: High", "Critical", "High", "Medium"],
    ["Likelihood: Medium", "High", "Medium", "Low"],
    ["Likelihood: Low", "Medium", "Low", "Low"],
]
SEVERITY_CLASSIFICATION_TABLE_COLUMNS: list[str] = ["Severity", "Impact: High", "Impact: Medium", "Impact: Low"]

FINDING_COUNT_TABLE_COLUMNS: list[str] = ["Severity", "Amount"]

RISK_CLASSIFICATION_MAIN_CONTENT_MD: str = """
| Severity               | Impact: High | Impact: Medium | Impact: Low |
| ---------------------- | ------------ | -------------- | ----------- |
| **Likelihood: High**   | Critical     | High           | Medium      |
| **Likelihood: Medium** | High         | Medium         | Low         |
| **Likelihood: Low**    | Medium       | Low            | Low         |
"""

RISK_CLASSIFICATION_IMPACT_CONTENT_MD: str = """
- High - leads to a significant material loss of assets in the protocol or significantly harms a group of users.

- Medium - leads to a moderate material loss of assets in the protocol or moderately harms a group of users.

- Low - leads to a minor material loss of assets in the protocol or harms a small group of users.
"""

RISK_CLASSIFICATION_LIKELIHOOD_CONTENT_MD: str = """
- High - attack path is possible with reasonable assumptions that mimic on-chain conditions, and the cost of the attack is relatively low compared to the amount of funds that can be stolen or lost.

- Medium - only a conditionally incentivized attack vector, but still relatively likely.

- Low - has too many or too unlikely assumptions or requires a significant stake by the attacker with little or no incentive.
"""

RISK_CLASSIFICATION_ACTION_REQUIRED_CONTENT_MD: str = """
- Critical - Must fix as soon as possible (if already deployed)

- High - Must fix (before deployment if not already deployed)

- Medium - Should fix

- Low - Could fix
"""