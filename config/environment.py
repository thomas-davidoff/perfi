import os
from enum import Enum
import warnings


class Environment(str, Enum):
    TESTING = "test"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


def get_environment() -> Environment:
    """Get the current environment based on PERFI_ENV variable."""
    env = os.environ.get("PERFI_ENV")
    if env is None:
        env = "dev"
        warnings.warn("PERFI_ENV is unset. Defaulting to 'dev' environment.")
    return Environment(env.lower())


ENVIRONMENT = get_environment()


if __name__ == "__main__":
    env = get_environment()
    print(env)
