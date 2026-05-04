# app/schemas/rag.py
"""
Pydantic schemas for RAG-related data structures.

TopicTree is the central output of topic extraction and the input to
topic distribution (distributor.py).
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class TopicEntry(BaseModel):
    name: str = Field(..., description="Topic name (e.g. 'Binary Search Trees')")
    subtopics: List[str] = Field(
        default_factory=list,
        description="2-5 specific subtopics within this topic",
    )
    estimated_weight: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Relative coverage weight in the syllabus (1=minimal, 5=extensive)",
    )
    bloom_affinity: List[str] = Field(
        default_factory=lambda: ["Remember", "Understand", "Apply"],
        description="Bloom's taxonomy levels typically tested for this topic",
    )


class UnitEntry(BaseModel):
    unit_number: int
    unit_name: str
    topics: List[TopicEntry]


class TopicTree(BaseModel):
    subject: str
    units: List[UnitEntry]

    @property
    def all_topics(self) -> List[TopicEntry]:
        """Flat list of all topics across all units."""
        return [topic for unit in self.units for topic in unit.topics]