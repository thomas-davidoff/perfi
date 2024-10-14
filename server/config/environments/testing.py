from .default import DefaultConfig
import os


class TestingConfig(DefaultConfig):
    name = "testing"

    def __init__(self, logger) -> None:
        super().__init__(logger)

        self.DEBUG = True
        self.TESTING = True

        database_uri = os.environ["DATABASE_URI"]
        if not database_uri:
            raise Exception("DATABASE_URI was not set.")
        self.SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URI"]
