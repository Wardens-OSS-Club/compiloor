from enum import Enum

from compiloor.services.logger import Logger


class Severity(Enum):
    """
        Enum class for severity levels.
    """
    
    GAS = 1
    QA = 2
    LOW = 3
    MEDIUM = 4
    HIGH = 5
    CRITICAL = 6
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return str(self)
    
    def cast_to_folder_sig(self: "Severity") -> "SeverityFolderIndex":
        mapping = {
            Severity.GAS: SeverityFolderIndex.GAS,
            Severity.QA: SeverityFolderIndex.QA,
            Severity.LOW: SeverityFolderIndex.LOW,
            Severity.MEDIUM: SeverityFolderIndex.MEDIUM,
            Severity.HIGH: SeverityFolderIndex.HIGH,
            Severity.CRITICAL: SeverityFolderIndex.CRITICAL,
        }
        return mapping[self]
    
    def cast_to_display_case(self: "Severity") -> str:
        mapping = {
            Severity.GAS: "GAS",
            Severity.QA: "QA",
            Severity.LOW: "Low",
            Severity.MEDIUM: "Medium",
            Severity.HIGH: "High",
            Severity.CRITICAL: "Critical",
        }
        return mapping[self]
    
class SeverityAnnotation(Enum):
    """Annotation class for severity levels."""
    GAS = "gas"
    QA = "qa"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    def cast_to_severity(self: "SeverityAnnotation") -> Severity:
        mapping = {
            SeverityAnnotation.GAS: Severity.GAS,
            SeverityAnnotation.QA: Severity.QA,
            SeverityAnnotation.LOW: Severity.LOW,
            SeverityAnnotation.MEDIUM: Severity.MEDIUM,
            SeverityAnnotation.HIGH: Severity.HIGH,
            SeverityAnnotation.CRITICAL: Severity.CRITICAL,
        }
        return mapping[self]
    
class SeverityFolderIndex(Enum):
    """Enum class for severity levels."""
    GAS = "GAS"
    QA = "QA"
    LOW = "L"
    MEDIUM = "M"
    HIGH = "H"
    CRITICAL = "C"
    
    def cast_to_severity(self: "SeverityFolderIndex") -> Severity:
        mapping = {
            SeverityFolderIndex.GAS: Severity.GAS,
            SeverityFolderIndex.QA: Severity.QA,
            SeverityFolderIndex.LOW: Severity.LOW,
            SeverityFolderIndex.MEDIUM: Severity.MEDIUM,
            SeverityFolderIndex.HIGH: Severity.HIGH,
            SeverityFolderIndex.CRITICAL: Severity.CRITICAL,
        }
        return mapping[self]
    
class FindingIdentifier():
    """
        A class that represents a finding identifier withing a severity of findings. i.e. [H-01]. \n
        Both [H-01] and H-01 are valid syntax.
    """
    
    index: int
    severity: Severity
    
    def __init__(self, finding_id: str) -> None:
        # Removes the brackets from the finding id:
        self.finding_id = finding_id.replace("[", "").replace("]", "")
    
        if self.finding_id.count("-") != 1:
            Logger.error("Finding id must contain exactly one '-' character.")
            exit(1)
        
        self.severity, self.index = self.finding_id.split("-")
        
        self.severity = SeverityFolderIndex.cast_to_severity(SeverityFolderIndex(self.severity))
        
        if not self.severity in Severity:
            Logger.error(f"Severity '{self.severity.name}' is invalid.")
            exit(1)
        
        for char in self.index:
            if char.isdigit(): continue
            Logger.error(f"Finding index '{self.index}' is invalid.")
            exit(1)
        
        self.index = int(self.index) if not self.index.startswith("0") else int(self.index[1:])
        
    def __str__(self) -> str:
        return self.finding_id

class FindingStatusAnnotation(Enum):
    """
        Annotation class for finding statuses.
    """
    ACKNOWLEDGED = "Acknowledged"
    UNRESOLVED = "Unresolved"
    DISPUTED = "Disputed"
    RESOLVED = "Resolved"
    PARTIALLY_RESOLVED = "Partially Resolved"
    