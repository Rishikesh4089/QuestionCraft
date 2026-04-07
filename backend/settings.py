import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env
load_dotenv()


class Settings(BaseSettings):
    """
    Fully compatible configuration loader for Pydantic v2.
    This version:
      ✅ Reads uppercase and lowercase env vars (auto-aliasing)
      ✅ Allows extra env vars safely
      ✅ Works with .env and system environment
    """

    # === API Keys ===
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

    # === Model Config ===
    GENERATION_MODEL_NAME: str = os.getenv("GENERATION_MODEL_NAME", "gpt-4.1")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
    EMBEDDING_BACKEND: str = os.getenv("EMBEDDING_BACKEND", "sentence_transformers")

    # === RAG Settings ===
    RAG_INDEX_DIR: str = os.getenv("RAG_INDEX_DIR", "./rag_index")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1200))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 80))
    USE_GPU: bool = os.getenv("USE_GPU", "true").lower() == "true"

    # === File Storage ===
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploaded_files")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")

    # === Debug ===
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # ✅ New Pydantic v2 way to configure env handling
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # allow unknown environment variables
        case_sensitive=False  # <--- ✅ key fix: ignore lowercase/uppercase differences
    )


# Instantiate global settings
settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.RAG_INDEX_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)

# Optional debug print
if settings.DEBUG_MODE:
    print("⚙️ Loaded Configuration:")
    for key, value in settings.model_dump().items():
        print(f"  {key}: {value}")
