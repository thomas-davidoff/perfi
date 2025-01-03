import typer
from .subparsers import subparsers
from perfi.entry import run as start_server


cli = typer.Typer(help="Perfi CLI Tool")


@cli.command("run")
def run():
    start_server()


for name, subparser in subparsers.items():
    cli.add_typer(subparser, name=name)


if __name__ == "__main__":
    cli()
