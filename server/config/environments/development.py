from .default import Config


class DevelopmentConfig(Config):
    def __init__(self) -> None:
        super().__init__()

        self.DEBUG = True
