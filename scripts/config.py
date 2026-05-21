import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate the project root (navigating up from the backend/src or scripts directory)
# This ensures python can find the .env file regardless of where the script is executed.
BASE_DIR = Path(__file__).resolve().parent.parent
if BASE_DIR.name == "src" or BASE_DIR.name == "scripts":
    BASE_DIR = BASE_DIR.parent

ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    """
    Centralized configuration management class utilizing Pydantic Settings.
    Automatically loads variables from .env file and performs type validation.
    """
    # Required parameters (system will fail-fast on startup if missing)
    openai_api_key: str = ""
    
    # Optional parameters with reliable production defaults
    embedding_model_name: str = "text-embedding-3-small"
    chroma_db_path: str = "./vector_db"
    chroma_collection_name: str = "mcg_diabetes_m130"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Configuration for Pydantic to hook into the .env file
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore" # Safely ignore extra env variables not declared above
    )

# Instantiate a global settings object for singleton pattern access across the application
settings = Settings()