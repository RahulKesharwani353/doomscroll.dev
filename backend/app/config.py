from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Doomscroll"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://doomscroll_user:doomscroll_password@localhost:5433/doomscroll"

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Background Jobs
    REFRESH_INTERVAL_MINUTES: int = 15
    FETCH_LIMIT_PER_SOURCE: int = 30
    SCHEDULER_ENABLED: bool = True

    # External APIs
    REDDIT_USER_AGENT: str = "Doomscroll/1.0"

    # Admin
    MIGRATION_API_KEY: str = "change-me-in-production"

    # CORS - use "*" to allow all origins, or comma-separated list of origins
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Cache
    CACHE_BACKEND: str = "memory"  # "memory" | "redis"
    CACHE_TTL_SHORT: int = 120     # 2 minutes - for frequently changing data (articles, search)
    CACHE_TTL_LONG: int = 600      # 10 minutes - for rarely changing data (sources, config)
    CACHE_REDIS_URL: str = "redis://localhost:6379"

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


# Global settings instance
settings = Settings()
