"""Configuration settings for the Cognify application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database - use PostgreSQL by default, fallback to SQLite
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cognify_user:cognify_password@db:5432/cognify_db"
    )
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Google Gemini API
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY", None)
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = "0.0.0.0"
    port: int = 3001
    frontend_url: str = "http://localhost:3011"
    
    # CORS
    allowed_origins: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3011,http://localhost:3000,http://localhost:8080,http://localhost:80"
    ).split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
