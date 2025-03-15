from sqlalchemy.engine.url import URL
from alembic.config import Config
from alembic.command import upgrade, downgrade, check

alembic_config = Config("alembic.ini")


# upgrade and downgrade serving as lambda-esque approach to run
# alembic migrations programmatically with async
# ripped from: https://github.com/sqlalchemy/alembic/discussions/991
def run_upgrade(connection, revision="head"):
    alembic_config.attributes["connection"] = connection
    upgrade(alembic_config, revision)


def run_downgrade(connection, revision="base"):
    alembic_config.attributes["connection"] = connection
    downgrade(alembic_config, revision)


def check_migrations(connection):
    alembic_config.attributes["connection"] = connection
    check(alembic_config)
