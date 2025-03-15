from sqlalchemy.engine.url import URL
from alembic.config import Config
from alembic.command import upgrade, downgrade

alembic_config = Config("alembic.ini")


def alembic_config_from_url(url: URL):
    alembic_config.set_main_option(
        "sqlalchemy.url", url.render_as_string(hide_password=False)
    )
    return alembic_config


# upgrade and downgrade serving as lambda-esque approach to run
# alembic migrations programmatically with async
# ripped from: https://github.com/sqlalchemy/alembic/discussions/991
def run_upgrade(connection, cfg, revision="head"):
    cfg.attributes["connection"] = connection
    upgrade(cfg, revision)


def run_downgrade(connection, cfg, revision="base"):
    cfg.attributes["connection"] = connection
    downgrade(cfg, revision)
