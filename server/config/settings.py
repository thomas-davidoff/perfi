from pydantic_settings import BaseSettings, SettingsConfigDict
import json


def fetch_external_secrets():
    """
    This is a placeholder for fetching secrets from an external source
    e.g. (bitwarden, aws sm, etc)
    """
    pass


ENVIRONMENT_FILE = ".env.local"  # set to whatever - just used for environment name


# The below values are set in the following order of precedence:
# 1. Set directly via env vars   command line or injected
# 2. Set via .env file           only searched if missing
# 3. Fallback defined here       only used if both above are missing
class BaseConfig(BaseSettings):
    ENVIRONMENT: str
    APP_NAME: str = "Perfi-API"
    model_config = SettingsConfigDict(env_file=ENVIRONMENT_FILE)


# create instance of BaseConfig to load ENVIRONMENT
base_config = BaseConfig()


class Settings(BaseSettings):
    """
    Dynamic settings class

    By this point, env vars may have been loaded.
    """

    # DB config
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str = "pfd"

    # App config
    APP_HOST: str
    APP_PORT: str
    UPLOAD_FOLDER: str

    # JWT config
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @classmethod
    def load_settings(cls):
        """
        Dynamically load settings based on environment,
        and returns an instance of the class.
        """
        if base_config.ENVIRONMENT in {"staging", "production"}:
            # in non-local configs, env vars should be injected to the container
            # or fetched directly from a secrets manager
            secrets = json.loads(fetch_external_secrets())
            return cls(**secrets)

        elif base_config.ENVIRONMENT == "development":
            # during local development, .env files are fine
            # the reason they are not being loaded in using python-dotenv
            # is because SettingsConfigDict gives use the added benefit
            # of detected "extra" env vars in a file

            # env vars injected or set directly are still given priority
            cls.model_config = SettingsConfigDict(
                env_file=f".env.{base_config.ENVIRONMENT}"
            )
            return cls()
        else:
            raise Exception(f"Unhandled environment {base_config.ENVIRONMENT}")
