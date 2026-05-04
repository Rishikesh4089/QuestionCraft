# app/core/exceptions.py
"""
Typed exception hierarchy for QuestionCraft.

All domain errors inherit from QuestionCraftError.
FastAPI exception handlers (registered in main.py) map these
to appropriate HTTP responses without leaking internal details.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class QuestionCraftError(Exception):
    """Base exception for all application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        *,
        detail: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail or message
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error_code,
            "message": self.message,
            "detail": self.detail,
        }


# ── Configuration ──────────────────────────────────────────────────────────

class ConfigurationError(QuestionCraftError):
    """Raised when required configuration is missing or invalid."""
    status_code = 500
    error_code = "CONFIGURATION_ERROR"


# ── File / Upload ───────────────────────────────────────────────────────────

class FileError(QuestionCraftError):
    """Base for file-related errors."""
    status_code = 400
    error_code = "FILE_ERROR"


class UnsupportedFileTypeError(FileError):
    status_code = 415
    error_code = "UNSUPPORTED_FILE_TYPE"


class FileReadError(FileError):
    status_code = 422
    error_code = "FILE_READ_ERROR"


class EmptyDocumentError(FileError):
    status_code = 422
    error_code = "EMPTY_DOCUMENT"


# ── RAG / Indexing ──────────────────────────────────────────────────────────

class IndexingError(QuestionCraftError):
    """Raised when index build fails."""
    status_code = 500
    error_code = "INDEXING_ERROR"


class IndexNotFoundError(QuestionCraftError):
    """Raised when retrieval is attempted before indexing."""
    status_code = 400
    error_code = "INDEX_NOT_FOUND"

    def __init__(self, message: str = "No syllabus index found. Upload and index files first.") -> None:
        super().__init__(message)


class RetrievalError(QuestionCraftError):
    """Raised when retrieval fails."""
    status_code = 500
    error_code = "RETRIEVAL_ERROR"


class EmbeddingError(QuestionCraftError):
    """Raised when embedding API call fails."""
    status_code = 502
    error_code = "EMBEDDING_ERROR"


# ── Generation ──────────────────────────────────────────────────────────────

class GenerationError(QuestionCraftError):
    """Raised when LLM generation fails after all retries."""
    status_code = 500
    error_code = "GENERATION_ERROR"


class PatternExtractionError(QuestionCraftError):
    """Raised when pattern extraction from PDF fails."""
    status_code = 422
    error_code = "PATTERN_EXTRACTION_ERROR"


class TopicExtractionError(QuestionCraftError):
    """Raised when topic extraction from syllabus fails."""
    status_code = 422
    error_code = "TOPIC_EXTRACTION_ERROR"


# ── Validation ──────────────────────────────────────────────────────────────

class PaperValidationError(QuestionCraftError):
    """Raised when generated paper fails structural validation."""
    status_code = 422
    error_code = "PAPER_VALIDATION_ERROR"


class RequestValidationError(QuestionCraftError):
    """Raised for malformed API request payloads."""
    status_code = 400
    error_code = "INVALID_REQUEST"


# ── External Services ────────────────────────────────────────────────────────

class OpenAIError(QuestionCraftError):
    """Wraps upstream OpenAI API errors."""
    status_code = 502
    error_code = "OPENAI_ERROR"


class CohereError(QuestionCraftError):
    """Wraps upstream Cohere API errors."""
    status_code = 502
    error_code = "COHERE_ERROR"