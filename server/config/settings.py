from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os


def fetch_external_secrets():
    """
    This is a placeholder for fetching secrets from an external source
    e.g. (bitwarden, aws sm, etc)
    """
    pass


class Settings(BaseSettings):
    """
    Dynamic settings class
    """

    # DB config
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str = "pfd"

    # App config
    APP_HOST: str = "0.0.0.0"
    APP_PORT: str
    UPLOAD_FOLDER: str
    APP_NAME: str = "perfi-api"

    # JWT config
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    @classmethod
    def load_settings(cls):
        """
        Dynamically load settings based on environment,
        and returns an instance of the class.
        """

        current_env = os.environ.get("ENVIRONMENT", "development")
        if current_env in {"staging", "production"}:
            # in non-local configs, env vars should be injected to the container
            # or fetched directly from a secrets manager
            secrets = json.loads(fetch_external_secrets())
            return cls(**secrets)

        elif current_env in {"development", "test"}:
            # during local development, .env files are fine
            # the reason they are not being loaded in using python-dotenv
            # is because SettingsConfigDict gives use the added benefit
            # of detected "extra" env vars in a file

            # env vars injected or set directly are still given priority
            cls.model_config = SettingsConfigDict(env_file=f".env.{current_env}")
            return cls()
        else:
            raise Exception(f"Unhandled environment {current_env}")
