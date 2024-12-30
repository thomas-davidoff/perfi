import subprocess
import os
import asyncio
import typer
from sqlalchemy.engine.url import make_url
from sqlalchemy import engine_from_config, pool, Engine
from sqlalchemy.sql import text
from alembic.config import Config
from alembic.runtime.migration import MigrationContext

from config.database import configure_alembic, get_database_urls
from perfi.core.database import Base, engine


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
def check_for_pending_migrations():
    """
    Check if there are pending migrations.
    """

    _, script, engine = configure_alembic()

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        latest_rev = script.get_current_head()

    if current_rev == latest_rev:
        print("Database is up-to-date.")
        return False
    else:
        print(
            f"Pending migrations detected. Current: {current_rev}, Latest: {latest_rev}"
        )
        return True
