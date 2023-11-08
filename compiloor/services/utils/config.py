from compiloor.services.logger.logger import Logger
from compiloor.services.utils.utils import validate_url


class ConfigUtils:
    """
        Miscellaneous functions for the configuration file.
    """
    
    # @audit Do we need a whole utility class for one static method?
    
    @staticmethod
    def validate_config_template_urls(config: dict) -> None:
        # Checking whether the keys are present:
        template_url_is_valid: bool = "template_url" in config         
        stylesheet_url_is_valid: bool = "stylesheet_url" in config
        
        # Checking whether the URLs are valid:
        if stylesheet_url_is_valid: stylesheet_url_is_valid = validate_url(config["stylesheet_url"])
        if template_url_is_valid: template_url_is_valid = validate_url(config["template_url"])

        if not template_url_is_valid and not stylesheet_url_is_valid:
            Logger.error("The template URL and the stylesheet URL must be valid URLs.")
            exit(1)
            
        if not template_url_is_valid:
            Logger.error("The template URL must be a valid URL.")
            exit(1)
            
        if not stylesheet_url_is_valid:
            Logger.error("The stylesheet URL must be a valid URL.")
            exit(1)