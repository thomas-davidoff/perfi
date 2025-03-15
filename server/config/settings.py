from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    PostgresDsn,
    BaseModel,
    computed_field,
)
from sqlalchemy.engine.url import URL
from typing import Annotated


__all__ = ["settings"]


class DatabaseSettings(BaseModel):
    HOST: str
    USER: str = "aksdjn"
    PASSWORD: str = "alksd"
    DATABASE: str = "akjnd"
    PORT: int = 23
    DRIVER: str = "postgresql+asyncpg"

    @computed_field(repr=False)
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
        env_nested_delimiter="__", env_file=".env", env_file_encoding="utf-8"
    )
    db: DatabaseSettings


settings = AppSettings()
