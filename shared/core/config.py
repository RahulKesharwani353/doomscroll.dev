import os
from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    """Shared settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://doomscroll_user:doomscroll_password@localhost:5433/doomscroll"

    # Debug
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from service-specific configs


# Global settings instance
settings = SharedSettings()
