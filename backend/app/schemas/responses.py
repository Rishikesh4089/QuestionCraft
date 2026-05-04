# app/schemas/responses.py
"""
Pydantic schemas for API responses.

All endpoints return one of these models for a consistent, typed response
envelope. FastAPI serialises them automatically via response_model=.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


class GeneratePaperResponse(BaseModel):
    """
    Returned by POST /generate-paper/.

    Contains the full PaperOutput dict plus the index_key so the
    frontend can use it for regeneration calls without re-uploading files.
    """
    index_key: str
    paper: Dict[str, Any]
    validation_errors: List[str] = []


class RegenerateQuestionResponse(BaseModel):
    success: bool
    new_question: Dict[str, Any]


class RegenerateSectionResponse(BaseModel):
    section: Dict[str, Any]


class ExtractPatternResponse(BaseModel):
    total_marks: int
    instructions: List[str]
    question_structure: List[Dict[str, Any]]


class IndexStatusResponse(BaseModel):
    indexed: bool
    index_key: str
    file_count: int


class ValidatePaperResponse(BaseModel):
    valid: bool
    errors: List[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str