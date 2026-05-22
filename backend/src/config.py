import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

SRC_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SRC_DIR.parent

class Settings(BaseSettings):
    openai_api_key: str = ""
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "utilization_review_db"
    
    embedding_model_name: str = "text-embedding-3-small"
    chroma_db_path: str = "./vector_db"
    chroma_collection_name: str = "medical_guidelines"
    
    # App Config
    environment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()