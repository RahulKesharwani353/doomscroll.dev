import os
from pydantic_settings import BaseSettings
from pydantic import field_validator


class SharedSettings(BaseSettings):
    """Shared settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DEBUG: bool = False

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError('DATABASE_URL must be set in environment variables')
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = SharedSettings()
