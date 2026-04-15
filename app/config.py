from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mode: Literal["DEV", "PROD"] = Field(default="DEV", alias="MODE")
    app_task: Literal["6.1", "6.2", "6.3", "6.4", "6.5", "7.1", "8.1", "8.2"] = Field(
        default="8.2",
        alias="APP_TASK",
    )
    docs_user: str = Field(default="docs", alias="DOCS_USER")
    docs_password: str = Field(default="docssecret", alias="DOCS_PASSWORD")

    jwt_secret: str = Field(default="change-me-in-production-use-long-random", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    database_path: str = Field(default="app.db", alias="DATABASE_PATH")

    @field_validator("mode", mode="before")
    @classmethod
    def strip_mode(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip().upper()
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_settings(settings: Settings) -> None:
    if settings.mode not in ("DEV", "PROD"):
        raise ValueError(f"MODE must be DEV or PROD, got {settings.mode!r}")
