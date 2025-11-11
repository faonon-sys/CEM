"""
Configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        json_schema_extra={
            "env_prefix": "",
        }
    )
    """Application settings loaded from environment variables."""

    # API Configuration
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "anthropic"

    # Database Configuration
    DATABASE_URL: str = "postgresql://reasoning_user:reasoning_pass@localhost:5432/reasoning_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "reasoning_db"
    DATABASE_USER: str = "reasoning_user"
    DATABASE_PASSWORD: str = "reasoning_pass"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Authentication & Security
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_COST_FACTOR: int = 12

    # Server Configuration
    BACKEND_URL: str = "http://localhost:8000"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5000
    API_PREFIX: str = "/api"
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5000,http://localhost:3000"

    # LLM Configuration
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4000
    LLM_RATE_LIMIT: int = 10
    LLM_TIMEOUT: int = 60

    # Feature Flags
    PHASE_1_ENABLED: bool = True
    PHASE_2_ENABLED: bool = True
    PHASE_3_ENABLED: bool = True
    PHASE_5_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


# Create global settings instance
settings = Settings()
