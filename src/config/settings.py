"""
Configuration settings for RYC Automation System
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Configuration (Ollama)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama server URL")
    OLLAMA_MODEL: str = Field(default="llama3.2:latest", description="Ollama model name - use format 'llama3.2:latest' or 'gemma2:2b'")
    MODEL_TEMPERATURE: float = Field(default=0.1, description="LLM temperature for classification consistency")
    
    # Gmail Configuration
    GMAIL_CREDENTIALS_PATH: str = Field(default="credentials.json", description="Path to Gmail credentials")
    GMAIL_TOKEN_PATH: str = Field(default="token.json", description="Path to Gmail token")
    
    # File Storage
    M_DRIVE_PATH: Path = Field(default="./test_drive", description="Path to shared M: drive (use ./test_drive for testing)")
    LOCAL_DOWNLOAD_PATH: Path = Field(default="./downloads", description="Temporary download location")
    
    # Vector Store (for RAG implementation)
    VECTOR_STORE_PATH: Path = Field(default="./vector_db", description="Vector database path")
    COLLECTION_NAME: str = Field(default="ryc_documents", description="Vector collection name")
    RAG_TRAINING_DOCS_PATH: Path = Field(default="./rag_training_docs", description="Training documents for RAG")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Path = Field(default="./logs/automation.log", description="Log file path")
    
    # API Settings (Phase 4)
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
