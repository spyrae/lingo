from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve once: repo_root/data (or /app/data in Docker).
_DEFAULT_DATA_DIR = str(Path(__file__).resolve().parents[2] / "data")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_bot_token: str = Field(description="Telegram Bot API token")
    db_path: str = Field(
        default="data/lingo.db",
        description="SQLite database path",
    )
    data_dir: str = Field(
        default=_DEFAULT_DATA_DIR,
        description="Root directory for content data (grammar, vocabulary, scenarios)",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for AI practice",
    )
    openai_model: str = Field(
        default="gpt-4.1-nano",
        description="OpenAI model for AI practice",
    )
    openai_timeout_seconds: int = Field(
        default=60,
        description="Timeout for OpenAI API call",
    )
    allowed_user_ids: list[int] = Field(
        default_factory=list,
        description="List of Telegram user IDs allowed to use the bot",
    )
    allow_all_users: bool = Field(
        default=False,
        description="Whether to allow access to all users",
    )


def get_settings() -> Settings:
    return Settings()
