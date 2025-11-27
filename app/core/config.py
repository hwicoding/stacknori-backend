from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Stacknori API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    version: str = "0.1.0"

    log_level: str = Field(default="info", alias="LOG_LEVEL")

    # Database
    database_url: str = Field(alias="DATABASE_URL")

    # Security
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_minutes: int = Field(
        default=60 * 24 * 14, alias="REFRESH_TOKEN_EXPIRE_MINUTES"
    )


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except PermissionError:
        return Settings(_env_file=None)

