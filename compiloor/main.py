if __name__ == "__main__":
    from typer import run as typer_run
    
    from compiloor.services.cli.cli import cli
        
    typer_run(cli())