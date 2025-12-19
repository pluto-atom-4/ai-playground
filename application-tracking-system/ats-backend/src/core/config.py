"""Configuration module for ATS backend application."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application metadata
    APP_NAME: str = "Application Tracking System"
    VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "NLP-powered application tracking and candidate matching system"

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ats_db"
    DATABASE_ECHO: bool = False

    # ChromaDB configuration for embeddings
    CHROMA_DB_PATH: str = "./data/chroma"

    # API Keys for LLMs
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # NLP Model configuration
    SPACY_MODEL: str = "en_core_web_sm"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a singleton instance
settings = Settings()

