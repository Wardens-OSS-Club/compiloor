from json import dumps

from os import makedirs
from os.path import expanduser, isfile, join

from compiloor.constants.environment import BASE_CONFIG_SCHEMA, COMPILOOR_CACHE_DIRECTORY, CONFIG_NAME

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
    
    @staticmethod
    def get_base_config_location() -> str:
        """
            Returns the location of the base config.
        """
        return join(
            expanduser('~'),
            '.cache',
            COMPILOOR_CACHE_DIRECTORY,
            CONFIG_NAME
        )
    
    @staticmethod
    def mutate_base_config(config: dict | str = BASE_CONFIG_SCHEMA, should_emit_log: bool = True) -> None:
        """
            Creates a default configuration file in the package root.
        """

        if isinstance(config, dict): config = dumps(config, indent=4)
        elif isfile(config): config = open(config).read()
        else: config = dumps(BASE_CONFIG_SCHEMA, indent=4)
        
        package_dir: str = ConfigUtils.get_base_config_location()

        if not isfile(package_dir):
            makedirs(package_dir.replace(CONFIG_NAME, ""))

        config_path: str = package_dir

        open(config_path, "w").write(config)
        
        if not should_emit_log: return 

        Logger.success(f"Successfully mutated the default config!")
        