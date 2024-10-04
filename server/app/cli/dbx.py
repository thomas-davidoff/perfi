# app/cli.py
import click
from flask.cli import AppGroup
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
import os
from urllib import parse

from initializers import db

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
