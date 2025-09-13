import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional # <-- Import Optional

# Load environment variables from a .env file for local development
load_dotenv()

class Settings(BaseSettings):
    """
    Manages the application's configuration using Pydantic BaseSettings.
    It loads settings from environment variables for security and flexibility.
    """
    # --- Standard OpenAI API Key ---
    # This is now the primary and only required credential for the LLM.
    # Set this in your .env file: OPENAI_API_KEY="sk-..."
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    # Model names for generation and embeddings. Using official OpenAI model names.
    GENERATION_MODEL_NAME: str = "gpt-4-turbo" # Updated to a common, modern model name
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    
    # --- MODIFIED LINE ---
    # Made GEMINI_API_KEY optional to prevent validation errors when it's not set.
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

    # Local storage paths
    FAISS_INDEX_PATH: str = "./faiss_indexes"
    UPLOAD_DIR: str = "./uploaded_files"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate settings for global access
settings = Settings()

# Ensure the necessary directories exist upon application startup
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)