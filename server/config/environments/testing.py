from .default import DefaultConfig


class TestingConfig(DefaultConfig):
    name = "testing"

    def __init__(self, logger) -> None:
        super().__init__(logger)

        self.DEBUG = True
        self.TESTING = True

        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
