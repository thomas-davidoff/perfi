from alembic.config import Config as AlembicConfig


def get_config():
    return AlembicConfig("alembic.ini")
