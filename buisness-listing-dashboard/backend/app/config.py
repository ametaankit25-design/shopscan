"""
config.py
---------
Reads environment variables (from backend/.env via python-dotenv)
and exposes a single Settings singleton used across the app.
"""
from __future__ import annotations

from functools import lru_cache
from urllib.parse import quote_plus

from pathlib import Path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str | None = None
    DB_USER: str = "listings_user"
    DB_PASSWORD: str  # Required - no default for security
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "listings_db"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @computed_field  # type: ignore[misc]
    @property
    def final_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            return url
        pw = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{pw}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            "?charset=utf8mb4"
        )

    @computed_field  # type: ignore[misc]
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
