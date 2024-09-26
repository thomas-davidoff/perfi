# NOTE - ALL OF THESE COMMANDS WILL REQUIRE SUPERUSER CREDENTIALS IN YOUR ACTIVE .env FILE!

# app/cli.py
import click
from flask.cli import AppGroup
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
import os
from urllib import parse

# TODO: Flask cli already has a db instance. Nest these commands under that db instance, by importing the existing commands and registering them here.
db_admin_cli_group = AppGroup("db_admin")


@db_admin_cli_group.command("create")
def db_setup():
    """Create the database and assign ownership to a new admin user."""

    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_pass = os.environ["DB_PASS"]

    print(db_name)
    print(os.getcwd())
    exit()

    encoded_password = parse.quote_plus(db_pass)

    uri = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/postgres"

    engine = create_engine(f"{uri}")

    try:
        with engine.connect() as connection:
            connection = connection.execution_options(isolation_level="AUTOCOMMIT")

            # Create database
            connection.execute(text(f"CREATE DATABASE {db_name} OWNER {db_user};"))
            click.echo(f"Database '{db_name}' created successfully.")

            # Grant privileges
            connection.execute(
                text(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
            )
            click.echo(f"Granted all privileges on '{db_name}' to '{db_user}'.")
    except ProgrammingError as e:
        click.echo(f"An error occurred: {e}")
    finally:
        engine.dispose()


@db_admin_cli_group.command("destroy")
def db_destroy():
    """Drop the database."""

    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_pass = os.environ["DB_PASS"]

    # URL-encode the password
    encoded_password = parse.quote_plus(db_pass)

    # Construct the admin URI (connecting to the 'postgres' database)
    uri = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/postgres"

    # Create an engine without default transaction management for admin tasks
    engine = create_engine(uri)

    try:
        # Establish a connection with autocommit enabled
        with engine.connect() as connection:
            # Enable autocommit for the connection
            connection = connection.execution_options(isolation_level="AUTOCOMMIT")

            # Check if the database exists
            result = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname;"),
                {"dbname": db_name},
            ).fetchone()

            if not result:
                click.echo(f"Database '{db_name}' does not exist.")
                return

            # Terminate all connections to the database
            connection.execute(
                text(
                    f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
            """
                )
            )
            click.echo(f"Terminated all connections to database '{db_name}'.")

            # Drop the database
            connection.execute(text(f"DROP DATABASE {db_name}"))
            click.echo(f"Database '{db_name}' dropped successfully.")

    except ProgrammingError as e:
        click.echo(f"Programming error: {e}")
    except OperationalError as e:
        click.echo(f"Operational error: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
    finally:
        engine.dispose()
