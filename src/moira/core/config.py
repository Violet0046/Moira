from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Moira", alias="MOIRA_APP_NAME")
    environment: str = Field(default="local", alias="MOIRA_ENV")
    debug: bool = Field(default=True, alias="MOIRA_DEBUG")
    api_prefix: str = Field(default="/api/v1", alias="MOIRA_API_PREFIX")
    host: str = Field(default="127.0.0.1", alias="MOIRA_HOST")
    port: int = Field(default=8000, alias="MOIRA_PORT")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/moira",
        alias="MOIRA_DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="MOIRA_REDIS_URL")
    default_model: str = Field(default="gpt-4.1", alias="MOIRA_DEFAULT_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
