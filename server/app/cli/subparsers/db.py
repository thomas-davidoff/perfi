import asyncio
import typer
from sqlalchemy.sql import text
from app.core.database import Base, engine
import subprocess
import os

db_cli = typer.Typer(help="Database management commands")


@db_cli.command("check")
def check():
    """Ping the database to check connectivity"""

    async def _check():
        try:
            async with engine.connect() as connection:
                result = await connection.execute(text("SELECT 1"))
                typer.echo(f"Database check result: {result.scalar()}")
                typer.echo("Database connection is OK.")
        except Exception as e:
            typer.echo(f"Database connection failed: {e}", err=True)

    asyncio.run(_check())


@db_cli.command("create")
def create_all():
    """Create all database tables."""

    async def _create():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        typer.echo("Database tables created.")

    asyncio.run(_create())


@db_cli.command("drop")
def drop_all():
    """Drop all database tables."""

    async def _drop():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        typer.echo("Database tables dropped.")

    asyncio.run(_drop())


@db_cli.command("sh")
def db_shell():
    """Open a database shell."""
    from sqlalchemy.engine.url import make_url
    from config.database import DATABASE_URL

    url = make_url(DATABASE_URL)
    command = [
        "psql",
        f"-h{url.host}",
        f"-p{url.port}",
        f"-U{url.username}",
        url.database,
    ]
    env = {**os.environ.copy(), "PGPASSWORD": url.password or ""}
    subprocess.call(command, env=env)


@db_cli.command("inspect")
def inspect_metadata():
    """Inspect registered tables in Base.metadata."""
    # from app.models import Account  # Import all models to ensure they are registered

    typer.echo("Inspecting Base.metadata...")
    typer.echo(f"Registered tables: {list(Base.metadata.tables.keys())}")
