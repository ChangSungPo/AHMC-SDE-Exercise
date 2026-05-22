import os
from pathlib import Path
from dotenv import load_dotenv

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent

root_env_path = project_root / ".env"

load_dotenv(dotenv_path=root_env_path)

class ScriptSettings:
    def __init__(self):
        # Fetch environment variables injected from the centralized file
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.chroma_db_path = os.getenv("CHROMA_DB_PATH", "")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "")
        self.chroma_collection_name = os.getenv("CHROMA_COLLECTION_NAME", "")

settings = ScriptSettings()