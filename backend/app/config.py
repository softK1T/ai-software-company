"""Application configuration and settings."""
from pydantic_settings import BaseSettings
from typing import Optional, Dict, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://dev:devpass@postgres:5432/aicompany"
    )

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")

    # GitHub
    github_app_id: Optional[str] = os.getenv("GITHUB_APP_ID")
    github_app_private_key: Optional[str] = os.getenv("GITHUB_APP_PRIVATE_KEY")
    github_installation_id: Optional[str] = os.getenv("GITHUB_INSTALLATION_ID")
    github_org: str = os.getenv("GITHUB_ORG", "softK1T")
    github_default_branch: str = os.getenv("GITHUB_DEFAULT_BRANCH", "main")

    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_org_id: Optional[str] = os.getenv("OPENAI_ORG_ID")

    # FastAPI
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_title: str = "AI Software Company Platform"
    api_version: str = "0.1.0"

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
