import os
from enum import Enum


class Environment(str, Enum):
    TESTING = "test"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


def get_environment() -> Environment:
    """Get the current environment based on PERFI_ENV variable."""
    env = os.environ.get("PERFI_ENV")
    if not env:
        raise UserWarning(
            "PERFI_ENV is unset. Must be set to 'test', 'dev', or 'prod'."
        )
    return Environment(env.lower())


ENVIRONMENT = get_environment()


if __name__ == "__main__":
    env = get_environment()
    print(env)
