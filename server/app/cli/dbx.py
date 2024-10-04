# app/cli.py
from flask.cli import AppGroup
import os
import os
import subprocess
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.engine.url import make_url

# TODO: Flask cli already has a db instance. Nest these commands under that db instance, by importing the existing commands and registering them here.
dbx_cli_group = AppGroup("dbx")


# These commands used for setting up or tearing down the database internally, and for detecting and performing migrations.
# use @with_app_context() or change the AppGroup above to a FlaskGroup to include Flask context.


@dbx_cli_group.command("seed")
def seed():
    """Use this command to seed the database with necessary data."""
    raise NotImplementedError


@dbx_cli_group.command("create")
def create():
    """Read models and create all."""
    raise NotImplementedError


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
