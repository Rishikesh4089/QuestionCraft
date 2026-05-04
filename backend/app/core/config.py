# app/core/config.py
"""
Typed, validated application configuration.
All settings come from environment variables or a .env file.
Application startup fails fast if required keys are missing.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "QuestionCraft API"
    APP_VERSION: str = "3.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = False
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_JSON: bool = False  # set True in production for structured JSON logs

    # ── Security ─────────────────────────────────────────────
    # CORS origins (comma-separated string or JSON list in env)
    CORS_ORIGINS: List[str] = Field(default=["*"])
    API_KEY_HEADER: Optional[str] = None  # If set, require X-API-Key header on all routes

    # ── OpenAI ───────────────────────────────────────────────
    OPENAI_API_KEY: str = Field(..., description="Required: OpenAI API key")
    GENERATION_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536  # Must match EMBEDDING_MODEL
    EMBED_BATCH_SIZE: int = 64
    ENRICHMENT_MODEL: str = "gpt-4o-mini"  # Cheap model for chunk tagging

    # ── Cohere (optional) ────────────────────────────────────
    COHERE_API_KEY: Optional[str] = None
    COHERE_RERANK_MODEL: str = "rerank-english-v3.0"

    # ── RAG Chunking ─────────────────────────────────────────
    CHUNK_SIZE_TOKENS: int = 400
    CHUNK_OVERLAP_TOKENS: int = 60

    # ── RAG Retrieval ────────────────────────────────────────
    RETRIEVAL_TOP_K: int = 10          # Candidates before reranking
    RERANK_TOP_N: int = 4              # Final chunks after reranking
    MAX_CONTEXT_TOKENS: int = 2000     # Token budget sent to LLM per question

    # ── RAG Enrichment ───────────────────────────────────────
    ENRICH_CHUNKS: bool = True
    ENRICHMENT_CONCURRENCY: int = 20   # Max concurrent enrichment calls

    # ── File Storage ─────────────────────────────────────────
    UPLOAD_DIR: str = "./uploaded_files"
    RAG_INDEX_DIR: str = "./rag_index"
    TEMP_DIR: str = "./temp"

    # ── OCR ──────────────────────────────────────────────────
    ENABLE_OCR: bool = True  # Requires pdf2image + tesseract installed

    # ── Generation ───────────────────────────────────────────
    MAX_RETRIES_QUESTION: int = 3
    SYLLABUS_MAX_TOKENS: int = 6000    # Token cap for topic extraction input
    TOPIC_EXTRACT_MAX_TOKENS: int = 5000

    # ── Rate Limiting ────────────────────────────────────────
    # Set to 0 to disable. Requires slowapi or equivalent.
    RATE_LIMIT_PER_MINUTE: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            # Support both comma-separated and JSON list formats
            import json
            stripped = v.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return v  # type: ignore[return-value]

    @model_validator(mode="after")
    def create_directories(self) -> "Settings":
        for path in (self.UPLOAD_DIR, self.RAG_INDEX_DIR, self.TEMP_DIR):
            os.makedirs(path, exist_ok=True)
        return self

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance. Import and call this everywhere."""
    return Settings()