import typer
from typing import Annotated
import subprocess
import os
import asyncio
import pytest
from sqlalchemy.engine.url import make_url
from sqlalchemy import engine_from_config, pool, Engine
from sqlalchemy.sql import text
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic import command

from config.database import configure_alembic, get_database_urls
from perfi.core.database import Base, engine
from perfi.entry import run as start_server

cli = typer.Typer(help="Perfi CLI Tool")


@cli.command("run")
def run():
    start_server()


DATABASE_URL_ASYNC, DATABASE_URL_SYNC = get_database_urls()
db_cli = typer.Typer(help="Database management commands")


@db_cli.command("ping")
def ping():
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


@db_cli.command("sh")
def db_shell():
    """Open a database shell."""

    url = make_url(DATABASE_URL_ASYNC)

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
    typer.echo("Inspecting Base.metadata...")
    typer.echo(f"Registered tables: {list(Base.metadata.tables.keys())}")


DATABASE_URL_ASYNC, DATABASE_URL_SYNC = get_database_urls()


def get_sync_engine() -> Engine:
    """
    Configure Alembic object with the same setup as env.py and return sync engine
    """

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", str(DATABASE_URL_SYNC))

    connectable = engine_from_config(
        {"sqlalchemy.url": str(DATABASE_URL_SYNC)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    return connectable


@db_cli.command("check")
def check_for_pending_migrations(silent: bool = False):
    """
    Check if there are pending migrations.
    """

    _, script, sync_engine = configure_alembic()

    with sync_engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        latest_rev = script.get_current_head()

    if current_rev == latest_rev:
        if not silent:
            print("Database is up-to-date.")
        return False
    else:
        if not silent:
            print(
                f"Pending migrations detected. Current: {current_rev}, Latest: {latest_rev}"
            )
        return True


@db_cli.command("upgrade")
def upgrade_to_latest(revision: str = "head"):
    """
    Perform the equivalent of 'alembic upgrade head' in Python.
    """

    has_revisions = check_for_pending_migrations(silent=True)

    alembic_config, _, sync_engine = configure_alembic()

    with sync_engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()

    if not has_revisions:
        print(f"Database is already up-to-date. Current DB revision is: {current_rev}")
        return

    command.upgrade(alembic_config, revision=revision)

    print("Database has been upgraded to the latest migration.")


@db_cli.command("drop")
def downgrade_to_base():
    """
    Downgrade the database back to before the first migration.
    """
    alembic_config, _, _ = configure_alembic()

    command.downgrade(alembic_config, "base")
    print("Database has been downgraded to the base (no migrations).")


@cli.command("test")
def run_tests(
    file_function: Annotated[str | None, typer.Argument()] = None,
    verbose: bool = True,
    stop_on_fail: bool = False,
):
    """
    Run pytest with custom options.
    """
    pytest_args = []
    if file_function:
        pytest_args.append(file_function)
    pytest.main(pytest_args)


cli.add_typer(db_cli, name="db")
