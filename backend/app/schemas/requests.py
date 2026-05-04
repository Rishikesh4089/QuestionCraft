# app/schemas/requests.py
"""
Pydantic schemas for API request bodies.

All Form-based endpoints parse JSON fields (like manual_pattern_json)
into these models for validation before passing to the service layer.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GeneratePaperRequest(BaseModel):
    """
    Parsed from the multipart form data in POST /generate-paper/.
    Not used directly as a FastAPI body model (the endpoint uses Form()),
    but used internally by the endpoint handler for clean validation.
    """
    subject: str
    difficulty_level: str = "Mixed"
    organization: Optional[str] = None
    program: Optional[str] = None
    course: Optional[str] = None
    exam_name: Optional[str] = None
    exam_date: Optional[str] = None
    manual_pattern: Optional[Dict[str, Any]] = None


class RegenerateQuestionRequest(BaseModel):
    subject: str
    section: str
    question_type: str
    topic: str
    subtopic: Optional[str] = None
    bloom_level: str = "Apply"
    difficulty_level: str = "Medium"
    marks: int = Field(default=5, ge=1)
    previous_questions: List[str] = Field(default_factory=list)
    # Index key returned from the original generate-paper call.
    # Pass this to skip file re-upload for regeneration.
    index_key: Optional[str] = None


class RegenerateSectionRequest(BaseModel):
    subject: str
    section: str
    question_type: str
    difficulty_level: str = "Medium"
    marks_each: int = Field(default=5, ge=1)
    # Existing questions in this section (to extract topics from)
    questions: List[Dict[str, Any]]
    index_key: Optional[str] = None


class ValidatePaperRequest(BaseModel):
    paper: Dict[str, Any]
    question_structure: List[Dict[str, Any]]
    expected_total_marks: int