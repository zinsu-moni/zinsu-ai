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

    BOT_TOKEN: str = Field(..., description="Telegram bot API token")
    OPENROUTER_API_KEY: str = Field(..., description="OpenRouter API token")
    DATABASE_URL: str = Field(..., description="Database connection URL")
    OWNER_TELEGRAM_ID: int = Field(..., description="Owner's Telegram ID for access control")
    ENVIRONMENT: Literal["development", "production", "testing"] = Field(
        "development", description="Execution environment"
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", description="Global logging level"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Ensures that the database URL starts with postgresql+asyncpg for async operations.
        If it starts with postgresql://, it is rewritten to postgresql+asyncpg://.
        """
        if not v:
            return v
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("sqlite://"):
            return v.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Cached getter for application Settings.
    """
    return Settings()
