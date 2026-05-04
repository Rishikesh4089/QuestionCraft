# app/schemas/pattern.py
"""
Pydantic schemas for paper pattern / structure.

PaperPattern is extracted from a reference PDF or specified manually.
It drives slot distribution and paper assembly.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SectionDef(BaseModel):
    """Definition of one section within the paper pattern."""
    section: str = Field(..., description="Section label (A, B, C, ...)")
    question_count: int = Field(..., ge=1)
    marks_each: int = Field(..., ge=1)
    question_type: str = Field(
        default="General",
        description="Short Answer | Long Answer | MCQ | General",
    )

    @property
    def section_total_marks(self) -> int:
        return self.question_count * self.marks_each


class PaperPattern(BaseModel):
    """
    Full structural specification of a question paper.

    Can be extracted from a PDF or provided manually via the API.
    """
    total_marks: int = Field(..., ge=1)
    instructions: List[str] = Field(default_factory=list)
    question_structure: List[dict] = Field(
        ...,
        description="List of section definitions (raw dicts for flexibility)",
    )

    def to_section_defs(self) -> List[SectionDef]:
        """Parse question_structure into validated SectionDef models."""
        return [SectionDef(**s) for s in self.question_structure]


class ManualPattern(BaseModel):
    """
    Simplified pattern specified directly by the API caller.
    """
    total_marks: int = Field(..., ge=1)
    instructions: Optional[List[str]] = None
    question_structure: Optional[List[dict]] = None