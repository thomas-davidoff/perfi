from .default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    name = "development"

    def __init__(self, logger=None) -> None:
        super().__init__(logger)

        self.DEBUG = True
