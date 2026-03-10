from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    codex_command: str = Field(
        default="codex",
        description="Codex CLI command name (e.g. codex)",
    )
    codex_timeout_seconds: int = Field(
        default=60,
        description="Timeout for Codex CLI call",
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

