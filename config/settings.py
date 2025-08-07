"""
Configuration settings for the AI-Driven Reverse Job Search Engine.
Uses Pydantic for type-safe configuration management.
"""

from typing import Optional, List
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "AI-Driven Reverse Job Search Engine"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/reverse_job_search",
        env="DATABASE_URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # AI/ML Model Configuration
    model_cache_dir: str = Field(
        default="./data/models",
        env="MODEL_CACHE_DIR"
    )
    bert_model_name: str = Field(
        default="bert-base-uncased",
        env="BERT_MODEL_NAME"
    )
    max_sequence_length: int = Field(default=512, env="MAX_SEQUENCE_LENGTH")
    
    # Job Data Sources
    job_apis: List[str] = Field(
        default=["indeed", "linkedin", "glassdoor"],
        env="JOB_APIS"
    )
    scraping_enabled: bool = Field(default=True, env="SCRAPING_ENABLED")
    
    # File Upload Configuration
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        default=[".pdf", ".docx", ".txt"],
        env="ALLOWED_FILE_TYPES"
    )
    upload_dir: str = Field(default="./data/raw/resumes", env="UPLOAD_DIR")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # External APIs
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    indeed_api_key: Optional[str] = Field(default=None, env="INDEED_API_KEY")
    linkedin_api_key: Optional[str] = Field(default=None, env="LINKEDIN_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
