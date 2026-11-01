from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: Literal["local", "production"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
