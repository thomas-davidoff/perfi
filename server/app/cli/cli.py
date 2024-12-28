import typer
from config import get_settings
import uvicorn
from .subparsers import subparsers


cli = typer.Typer(help="Perfi CLI Tool")


@cli.command("run")
def run():
    """Run the dev instance"""
    print("running dev instance")
    api_settings = get_settings()
    uvicorn.run(
        "app:app",
        host=api_settings.APP_HOST,
        port=int(api_settings.APP_PORT),
        reload=True,
    )


for name, subparser in subparsers.items():
    cli.add_typer(subparser, name=name)


if __name__ == "__main__":
    cli()
