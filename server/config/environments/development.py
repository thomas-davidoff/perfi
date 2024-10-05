from .default import Config
from config import logger


class DevelopmentConfig(Config):
    def __init__(self) -> None:
        super().__init__()

        logger.debug("Loading development config...")

        self.DEBUG = True
