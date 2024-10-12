from .default import DefaultConfig


class TestingConfig(DefaultConfig):
    name = "testing"

    def __init__(self, logger) -> None:
        super().__init__(logger)

        self.DEBUG = True
        self.TESTING = True

        # self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        # self.SQLALCHEMY_DATABASE_URI = (
        #     "postgresql+psycopg2://poopy:12345@127.0.0.1:8888/tests"
        # )

        self.SQLALCHEMY_DATABASE_URI = (
            "postgresql://postgres:mysecretpassword@localhost:5432/testdb"
        )
