import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Doomscroll"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    REFRESH_INTERVAL_MINUTES: int = 15
    FETCH_LIMIT_PER_SOURCE: int = 30
    SCHEDULER_ENABLED: bool = True
    REDDIT_USER_AGENT: str = "Doomscroll/1.0"
    MIGRATION_API_KEY: str = os.getenv("MIGRATION_API_KEY", "")
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    CACHE_BACKEND: str = "memory"
    CACHE_TTL_SHORT: int = 120
    CACHE_TTL_LONG: int = 600
    CACHE_REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTH_REQUESTS: int = 5
    RATE_LIMIT_API_REQUESTS: int = 100

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError(
                'DATABASE_URL must be set in environment variables')
        return v

    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v:
            raise ValueError(
                'JWT_SECRET_KEY must be set in environment variables')
        if len(v) < 10:
            raise ValueError('JWT_SECRET_KEY must be at least 10 characters')
        return v

    @field_validator('MIGRATION_API_KEY')
    @classmethod
    def validate_migration_key(cls, v: str) -> str:
        if not v:
            raise ValueError(
                'MIGRATION_API_KEY must be set in environment variables')
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        origins = self.CORS_ORIGINS.strip()
        if origins == "*":
            return ["*"]
        return [origin.strip() for origin in origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
