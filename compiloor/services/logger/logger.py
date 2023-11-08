from rich import print as rich_print


class Logger:
    """
        Static class used for logging pretty error messages to the console.
        All of its methods are static.
    """
    
    @staticmethod
    def error(message: str = "", *args, **kwargs) -> None:
        rich_print(f"[bold red]Error: [/bold red][white]{message}", *args, **kwargs)

    @staticmethod
    def warning(message: str = "", *args, **kwargs) -> None:
        rich_print(f"[bold yellow]Warning: [/bold yellow][white]{message}", *args, **kwargs)
        
    @staticmethod
    def QA(message: str = "", *args, **kwargs) -> None:
        rich_print(f"[bold blue]QA: [/bold blue][white]{message}", *args, **kwargs)
        
    @staticmethod
    def success(message: str = "", *args, **kwargs) -> None:
        rich_print(f"[bold green]Success: [/bold green][white]{message}", *args, **kwargs)