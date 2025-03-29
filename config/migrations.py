from alembic.config import Config
from alembic.command import upgrade, downgrade, check
import io

alembic_config = Config("alembic.ini")


# upgrade and downgrade serving as lambda-esque approach to run
# alembic migrations programmatically with async
# ripped from: https://github.com/sqlalchemy/alembic/discussions/991
def run_upgrade(connection, cfg: Config, revision="head"):
    cfg.attributes["connection"] = connection
    upgrade(cfg, revision)


def run_downgrade(connection, cfg, revision="base"):
    cfg.attributes["connection"] = connection
    downgrade(cfg, revision)


def check_migrations(connection, cfg: Config, silent=False):
    cfg.attributes["connection"] = connection

    if silent:
        og_stdout = cfg.stdout
        cfg.stdout = io.StringIO()

    check(cfg)

    if silent:
        cfg.stdout = og_stdout
