from compiloor.services.parser.markdown import create_html_from_markdown
from compiloor.constants.environment import FINDING_RESOLUTION_STATUS_HEADING
from compiloor.services.logger import Logger
from compiloor.services.typings.finding import Severity, SeverityFolderIndex, FindingStatusAnnotation

class Finding:
    """
        A class that represents a serialized finding.
    """
    
    id: str # The ID of the finding. Example: "[H-01]".
    id_num: int # The number of the finding in the severity it belongs to.
    
    title: str
    severity: Severity
    status: FindingStatusAnnotation
    
    fragment: str
    
    # The to-be-rendered HTML fragment of the finding. It includes rendered code blocks. 
    # This is the fragment that will be inserted into the report.
    render_fragment: str 
    
    def __init__(self, fragment: str) -> None:
        self.fragment = fragment
        _fragment: list[str] = fragment.split("\n")
        first_row = _fragment[0]
        
        if not "[" in first_row or not "]" in first_row:
            Logger.error(f"Invalid finding fragment: {first_row}")
            exit(1)
        
        fragments: list[str] = first_row.split("]")
        
        # Case where a finding does not have a title:
        if fragments[1] == "": 
            Logger.warning(f"Finding title is missing: {first_row}")
            fragments[1] = "-"
            _fragment[0] = fragments[0] + "] -"
        
        self.fragment = "\n".join(_fragment)
        
        self.id = fragments[0].split("[")[1].strip() # The ID without the brackets.
        self.id_num = int(self.id.split("-")[1].strip()) # The ID's number as an integer.
        
        self.title = fragments[1].strip() # Only the title without the ID.
        self.severity = SeverityFolderIndex.cast_to_severity(SeverityFolderIndex(self.id.split("-")[0].strip().upper()))
        self.status = None
        
        # Getting the resolution status from the finding if there is one or setting it to the default if not:
        if FINDING_RESOLUTION_STATUS_HEADING in self.fragment:
            
            _resolution_status_fragment = self.fragment.split(FINDING_RESOLUTION_STATUS_HEADING)[1].strip()
            if _resolution_status_fragment == "{{resolution_status}}": 
                self.fragment = self.fragment.replace(_resolution_status_fragment, FindingStatusAnnotation.RESOLVED.value)
                _resolution_status_fragment = FindingStatusAnnotation.RESOLVED
                
            self.status = FindingStatusAnnotation(_resolution_status_fragment) # Parsing the resolution status and checking for validity. Throws an error if the status is invalid.

            self.fragment = self.fragment.replace(FINDING_RESOLUTION_STATUS_HEADING + self.status.value, "")

        if not self.status: self.status = FindingStatusAnnotation.UNRESOLVED # Resolved is the default status. TODO: Make this configurable.

        # TODO: Abstract away the CSS classes into a modular system.
        # The fragment used for adding to the report:
        # Contains the rendered markdown and code blocks rendered with pygments for syntax-highlighting:
        self.render_fragment = f'''
            <div id="section-8-[[{self.severity.value}_severity_index]]-{self.id_num}" class="finding">
                {create_html_from_markdown(self.fragment)}
            </div>
        '''