# app/cli.py
from flask.cli import AppGroup
import os
import os
import subprocess
from flask import current_app
from sqlalchemy.engine.url import make_url
from database import db, seed_all, unseed_all

# TODO: Flask cli already has a db instance. Nest these commands under that db instance, by importing the existing commands and registering them here.
dbx_cli_group = AppGroup("dbx")


# These commands used for setting up or tearing down the database internally, and for detecting and performing migrations.
# use @with_app_context() or change the AppGroup above to a FlaskGroup to include Flask context.
# change to above - nah; don't need app context. app group already provides it.


@dbx_cli_group.command("seed")
def seed():
    """Use this command to seed the database with necessary data."""
    seed_all()


@dbx_cli_group.command("unseed")
def seed():
    """Use this command to UNseed the database."""
    unseed_all()


# Usage: `Flask dbx shell`
@dbx_cli_group.command("shell")
# @with_appcontext
def psql_shell():
    """Opens a psql shell connected to the database."""
    # parse the uri to make sure it doesn't misinterpret literal @ symbols
    database_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]

    url = make_url(database_uri)

    db_name = url.database
    user = url.username
    password = url.password
    host = url.host
    port = str(url.port)

    command = ["psql", f"-h{host}", f"-p{port}", f"-U{user}", db_name]

    # copy env for subprocess and set PGPASSWORD (it's expected to pass the prompt)
    env = {**os.environ.copy(), **{"PGPASSWORD": password}}

    # Run the psql command
    subprocess.call(command, env=env)


@dbx_cli_group.command("create")
def create_all():
    """Runs the `create_all` command; creates all defined tables."""
    db.create_all()


@dbx_cli_group.command("drop")
def drop_all():
    """Drops all the tables."""
    db.drop_all()
