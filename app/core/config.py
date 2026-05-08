"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_TITLE: str = "Salesforce Identity Validator"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Validates Salesforce user registrations against identity documents"
    DEBUG: bool = False
    
    # Azure Configuration
    AZURE_ENDPOINT: str
    AZURE_API_KEY: str
    AZURE_API_VERSION: str = "2024-11-30"
    AZURE_ANALYZER_ID: str = "prebuilt-idDocument"
    
    # Validation Configuration
    MIN_NAME_MATCH_SCORE: float = 85.0  # Fuzzy match score threshold (0-100)
    POLLING_MAX_ATTEMPTS: int = 60
    POLLING_INTERVAL_MS: int = 2000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Security
    API_KEYS: list = []  # Optional API keys for authentication
    ALLOWED_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()


def setup_logging():
    """Configure structured logging"""
    settings = get_settings()
    
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    if settings.LOG_FORMAT == "json":
        # Configure JSON logging
        import json
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": logging.Formatter.formatTime(self, record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        
        formatter = JsonFormatter()
    else:
        # Configure text logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
