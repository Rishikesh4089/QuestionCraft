# app/schemas/paper.py
"""
Pydantic schemas for question paper data.

These are the core domain models — Question, Section, PaperOutput —
used throughout generation and returned as API responses.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Question(BaseModel):
    text: str = Field(..., description="Full question text (including MCQ options if applicable)")
    marks: int = Field(..., ge=1, description="Marks allocated to this question")
    blooms_taxonomy_level: str = Field(..., description="Bloom's taxonomy level")
    topic: str = Field(..., description="Topic from the syllabus")


class Section(BaseModel):
    section: str = Field(..., description="Section label (A, B, C, ...)")
    question_type: str = Field(..., description="Question type for this section")
    questions: List[Question]

    @property
    def total_marks(self) -> int:
        return sum(q.marks for q in self.questions)


class PaperOutput(BaseModel):
    """Complete generated question paper."""
    organization: str = ""
    program: str = ""
    course: str = ""
    exam_name: str = ""
    exam_date: str = ""
    subject: str
    total_marks: int
    instructions: List[str] = Field(default_factory=list)
    sections: List[Section]

    @property
    def computed_total_marks(self) -> int:
        return sum(s.total_marks for s in self.sections)


class QuestionSlot(BaseModel):
    """
    Internal planning unit — fully specifies one question to be generated.
    Created by the distributor, consumed by the section generator.
    """
    section: str
    slot_index: int          # 0-indexed position within the section
    topic: str
    subtopic: str
    bloom_level: str
    marks: int
    question_type: str
    difficulty: str