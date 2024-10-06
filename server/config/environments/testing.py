from .default import Config
from config import logger


class TestingConfig(Config):
    def __init__(self) -> None:
        super().__init__()

        logger.debug("Loading testing config...")

        self.DEBUG = True
        self.TESTING = True

        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
