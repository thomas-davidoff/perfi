from config.environment import ENVIRONMENT, Environment
from datetime import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    AfterValidator,
    PostgresDsn,
    BaseModel,
    computed_field,
    BeforeValidator,
)
from sqlalchemy.engine.url import URL
from typing import Annotated
from functools import cached_property
import logging


def minutes_to_timedelta(v: int) -> timedelta:
    print(f"receiving value: {v}")
    if not isinstance(v, int):
        raise ValueError("Must be an integer.")
    if not v > 0:
        raise ValueError("Must be greater than 0")
    return timedelta(minutes=v)


class DatabaseSettings(BaseModel):
    HOST: str = "localhost"
    PASSWORD: str
    USER: str = "perfi"
    DATABASE: str = "perfi"
    PORT: int = 5432
    DRIVER: str = "postgresql+asyncpg"

    @computed_field(repr=False)
    @cached_property
    def url(self) -> Annotated[URL, PostgresDsn]:
        url = URL.create(
            username=self.USER,
            password=self.PASSWORD,
            database=self.DATABASE,
            port=self.PORT,
            host=self.HOST,
            drivername=self.DRIVER,
        )
        PostgresDsn(url.render_as_string(hide_password=False))
        return url


def coerce_to_timedelta(v: int) -> timedelta:
    try:
        minutes = int(v)
    except ValueError as e:
        raise ValueError("Expires in minutes must be a valid integer.") from e

    if not minutes > 0:
        raise ValueError("Expires in minutes must be gte 0.")

    return timedelta(minutes=minutes)


class JWTSettings(BaseModel):
    REFRESH_TOKEN_EXPIRES_IN_MINUTES: Annotated[
        timedelta, BeforeValidator(coerce_to_timedelta)
    ]
    ACCESS_TOKEN_EXPIRES_IN_MINUTES: Annotated[
        timedelta, BeforeValidator(coerce_to_timedelta)
    ]

    SECRET_KEY: str
    ALGO: str = "HS256"


def validate_log_level(v: str) -> str:
    if v.upper() not in logging.getLevelNamesMapping():
        raise ValueError(
            f"Invalid log level '{v}'. Must be one of {', '.join(logging.getLevelNamesMapping().keys())}"
        )
    return v.upper()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=[".env", f".env.{ENVIRONMENT.value}"],
        env_file_encoding="utf-8",
        populate_by_name=True,
    )
    ENV: Environment = ENVIRONMENT
    jwt: JWTSettings
    db: DatabaseSettings

    LOG_LEVEL: Annotated[str, AfterValidator(validate_log_level)] = "WARNING"

    PWD_HASH_ROUNDS: int = 12


settings = AppSettings()

if __name__ == "__main__":
    print(settings)
    print(settings.LOG_LEVEL)
