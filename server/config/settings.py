from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    PostgresDsn,
    BaseModel,
    computed_field,
)
from sqlalchemy.engine.url import URL
from typing import Annotated
from functools import cached_property
import os


# __all__ = ["settings"]


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


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_file=[".env", f'.env.{os.getenv("PERFI_ENV")}'],
        env_file_encoding="utf-8",
    )
    db: DatabaseSettings


settings = AppSettings()


if __name__ == "__main__":
    print(settings)
