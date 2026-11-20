from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ENVIRONMENT: Literal["local", "production"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
