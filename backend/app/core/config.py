"""
Configuration module for Product Hunter AI.
Loads environment variables and provides typed configuration settings.
"""

from pydantic import BaseSettings, Field, validator
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Product Hunter AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Database
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="product_hunter", env="POSTGRES_DB")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")

    # Redis
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_ALERT_CHAT_ID: str = Field(..., env="TELEGRAM_ALERT_CHAT_ID")

    # AI Provider
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")
    LLM_MODEL: str = Field(default="gpt-4o", env="LLM_MODEL")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # Exchange Rates API (for currency conversion)
    EXCHANGE_RATES_API_KEY: Optional[str] = Field(default=None, env="EXCHANGE_RATES_API_KEY")

    # Scraping/API keys for marketplaces (where available)
    ALIBABA_API_KEY: Optional[str] = Field(default=None, env="ALIBABA_API_KEY")
    ALIEXPRESS_API_KEY: Optional[str] = Field(default=None, env="ALIEXPRESS_API_KEY")
    AMAZON_EG_ACCESS_KEY: Optional[str] = Field(default=None, env="AMAZON_EG_ACCESS_KEY")
    JUMIA_API_KEY: Optional[str] = Field(default=None, env="JUMIA_API_KEY")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()