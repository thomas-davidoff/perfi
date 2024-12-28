from .default import DefaultConfig


class DevelopmentConfig(DefaultConfig):
    name = "development"

    def __init__(self) -> None:
        super().__init__()

        self.DEBUG = True
