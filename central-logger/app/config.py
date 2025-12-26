"""
Configuration management using environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os
import json


class Settings(BaseSettings):
    # Service Info
    SERVICE_NAME: str = "central-logger"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database
    DATABASE_URL: str
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: List[str] = ["*"]  # Configure properly for production
    
    # API Keys Storage (In production, use database)
    # Format: {"client_secret_key": "client_id"}
    API_KEYS: dict = {}
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    @field_validator('API_KEYS', mode='before')
    @classmethod
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
