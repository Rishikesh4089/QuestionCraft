# app/services/paper_service.py
"""
PaperService — orchestrates full question paper generation.

This is the only place that assembles all generation components together.
API handlers call exactly one method here and return the result.

Flow for generate():
  1.  Ensure syllabus files are indexed (cached — never re-indexed per request)
  2.  Extract topic tree from syllabus text
  3.  Resolve paper pattern (PDF extraction | manual | default)
  4.  Distribute topics into QuestionSlots (deterministic, seeded)
  5.  Group slots by section
  6.  Generate sections in parallel (asyncio.gather)
     └─ Within each section: generate questions sequentially (for dedup)
  7.  Assemble PaperOutput
  8.  Validate structure and marks
  9.  Targeted repair: regenerate only broken sections (not the full paper)
  10. Return dict + index_key
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from  app.core.config import Settings
from  app.generation.distributor import distribute_topics
from  app.generation.pattern_extractor import extract_pattern
from  app.generation.query_generator import generate_queries
from  app.generation.question_generator import generate_question
from  app.generation.topic_extractor import extract_topics
from  app.generation.validator import validate_paper
from  app.rag.indexer.chunker import count_tokens, decode, encode
from  app.rag.loaders.registry import load_document
from  app.rag.pipeline import RAGPipeline
from  app.schemas.paper import PaperOutput, Question, QuestionSlot, Section
from  app.schemas.pattern import ManualPattern, PaperPattern

logger = logging.getLogger(__name__)

_DEFAULT_QUESTION_STRUCTURE = [
    {"section": "A", "question_count": 5, "marks_each": 4,  "question_type": "Short Answer"},
    {"section": "B", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
    {"section": "C", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
]
_DEFAULT_TOTAL_MARKS = 80
_DEFAULT_INSTRUCTIONS = ["Answer all questions."]


class PaperService:
    """
    Stateless orchestrator for paper generation.

    Receives a RAGPipeline and AsyncOpenAI client via constructor injection —
    both are application-scoped singletons created at startup.
    """

    def __init__(
        self,
        rag: RAGPipeline,
        client: AsyncOpenAI,
        settings: Settings,
    ) -> None:
        self._rag = rag
        self._client = client
        self._settings = settings

    # ── Public: generate full paper ───────────────────────────────────────

    async def generate(
        self,
        subject: str,
        syllabus_paths: List[Path],
        difficulty: str = "Mixed",
        manual_pattern: Optional[ManualPattern] = None,
        pattern_pdf_path: Optional[Path] = None,
        organization: str = "",
        program: str = "",
        course: str = "",
        exam_name: str = "",
        exam_date: str = "",
    ) -> Dict[str, Any]:
        """
        Generate a complete question paper.

        Returns a dict with keys: index_key, paper (dict), validation_errors (list).
        """
        logger.info(f"Paper generation start: subject={subject!r}, difficulty={difficulty}")

        # ── 1. Index ───────────────────────────────────────────────────────
        index_key = await self._rag.ensure_indexed(syllabus_paths)
        logger.info(f"Index ready: key={index_key}")

        # ── 2. Resolve pattern ─────────────────────────────────────────────
        pattern = await self._resolve_pattern(manual_pattern, pattern_pdf_path)

        # ── 3. Extract topics ──────────────────────────────────────────────
        syllabus_text = self._load_syllabus_text(syllabus_paths)
        topic_tree = await extract_topics(
            syllabus_text=syllabus_text,
            subject_hint=subject,
            client=self._client,
            settings=self._settings,
        )

        # ── 4. Distribute slots ────────────────────────────────────────────
        slots = distribute_topics(
            topic_tree=topic_tree,
            question_structure=pattern.question_structure,
            difficulty=difficulty,
        )

        # ── 5. Group slots by section ──────────────────────────────────────
        section_slots: Dict[str, List[QuestionSlot]] = {}
        for slot in slots:
            section_slots.setdefault(slot.section, []).append(slot)

        ordered_sections = [s["section"] for s in pattern.question_structure]

        # ── 6. Generate sections in parallel ──────────────────────────────
        logger.info(f"Generating {len(ordered_sections)} sections in parallel…")
        tasks = [
            self._generate_section(
                section_name=name,
                slots=section_slots.get(name, []),
                index_key=index_key,
                subject=subject,
            )
            for name in ordered_sections
            if name in section_slots
        ]
        sections: List[Section] = list(await asyncio.gather(*tasks))

        # ── 7. Assemble paper ──────────────────────────────────────────────
        paper = PaperOutput(
            organization=organization,
            program=program,
            course=course,
            exam_name=exam_name,
            exam_date=exam_date,
            subject=subject,
            total_marks=pattern.total_marks,
            instructions=pattern.instructions or _DEFAULT_INSTRUCTIONS,
            sections=sections,
        )

        # ── 8. Validate ────────────────────────────────────────────────────
        paper_dict = paper.model_dump()
        errors = validate_paper(
            sections=paper_dict["sections"],
            question_structure=pattern.question_structure,
            expected_total_marks=pattern.total_marks,
        )

        if errors:
            logger.warning(f"Validation issues ({len(errors)}): {errors}")
            # ── 9. Targeted repair ─────────────────────────────────────────
            paper = await self._repair(
                paper=paper,
                errors=errors,
                section_slots=section_slots,
                ordered_sections=ordered_sections,
                index_key=index_key,
                subject=subject,
            )
            paper_dict = paper.model_dump()
            errors = validate_paper(
                sections=paper_dict["sections"],
                question_structure=pattern.question_structure,
                expected_total_marks=pattern.total_marks,
            )

        logger.info(
            f"Paper generation complete: {len(paper.sections)} sections, "
            f"{paper.computed_total_marks} marks"
        )
        return {
            "index_key": index_key,
            "paper": paper_dict,
            "validation_errors": errors,
        }

    # ── Public: regenerate single question ────────────────────────────────

    async def regenerate_question(
        self,
        index_key: str,
        subject: str,
        topic: str,
        subtopic: str,
        question_type: str,
        bloom_level: str,
        marks: int,
        difficulty: str = "Medium",
        previous_questions: Optional[List[str]] = None,
    ) -> Question:
        """Regenerate a single question using an existing index."""
        queries = await generate_queries(
            topic=topic,
            subtopic=subtopic,
            question_type=question_type,
            bloom_level=bloom_level,
            client=self._client,
            settings=self._settings,
        )
        chunks = await self._rag.retrieve(
            queries=queries,
            index_key=index_key,
            top_k=self._settings.RETRIEVAL_TOP_K,
            rerank_top_n=self._settings.RERANK_TOP_N,
            max_context_tokens=self._settings.MAX_CONTEXT_TOKENS,
        )
        context = self._rag.build_context(chunks) if chunks else f"Topic: {topic} — {subtopic}"

        return await generate_question(
            context=context,
            subject=subject,
            topic=topic,
            subtopic=subtopic,
            question_type=question_type,
            bloom_level=bloom_level,
            marks=marks,
            difficulty=difficulty,
            previous_questions=previous_questions or [],
            client=self._client,
            settings=self._settings,
        )

    # ── Public: regenerate entire section ─────────────────────────────────

    async def regenerate_section(
        self,
        index_key: str,
        subject: str,
        section_name: str,
        question_type: str,
        existing_questions: List[Dict[str, Any]],
        marks_each: int = 5,
        difficulty: str = "Medium",
    ) -> Section:
        """Regenerate all questions in a section from existing question metadata."""
        slots = [
            QuestionSlot(
                section=section_name,
                slot_index=i,
                topic=q.get("topic", "General"),
                subtopic=q.get("subtopic") or q.get("topic", "General"),
                bloom_level=q.get("blooms_taxonomy_level", "Apply"),
                marks=marks_each,
                question_type=question_type,
                difficulty=difficulty,
            )
            for i, q in enumerate(existing_questions)
        ]
        return await self._generate_section(
            section_name=section_name,
            slots=slots,
            index_key=index_key,
            subject=subject,
        )

    # ── Private: section generator ────────────────────────────────────────

    async def _generate_section(
        self,
        section_name: str,
        slots: List[QuestionSlot],
        index_key: str,
        subject: str,
    ) -> Section:
        """
        Generate all questions for one section.

        Questions are generated sequentially within a section so each
        question can see the previously generated ones for deduplication.
        Sections themselves run in parallel (called via asyncio.gather).
        """
        questions: List[Question] = []
        previous_texts: List[str] = []

        for slot in slots:
            queries = await generate_queries(
                topic=slot.topic,
                subtopic=slot.subtopic,
                question_type=slot.question_type,
                bloom_level=slot.bloom_level,
                client=self._client,
                settings=self._settings,
            )
            chunks = await self._rag.retrieve(
                queries=queries,
                index_key=index_key,
                top_k=self._settings.RETRIEVAL_TOP_K,
                rerank_top_n=self._settings.RERANK_TOP_N,
                max_context_tokens=self._settings.MAX_CONTEXT_TOKENS,
            )
            context = (
                self._rag.build_context(chunks)
                if chunks
                else f"Topic: {slot.topic} — {slot.subtopic}"
            )

            question = await generate_question(
                context=context,
                subject=subject,
                topic=slot.topic,
                subtopic=slot.subtopic,
                question_type=slot.question_type,
                bloom_level=slot.bloom_level,
                marks=slot.marks,
                difficulty=slot.difficulty,
                previous_questions=previous_texts,
                client=self._client,
                settings=self._settings,
            )
            questions.append(question)
            previous_texts.append(question.text)

            logger.info(
                f"  ✓ {section_name}[{slot.slot_index + 1}] "
                f"{slot.topic} [{slot.bloom_level}] {slot.marks}m"
            )

        return Section(
            section=section_name,
            question_type=slots[0].question_type if slots else "General",
            questions=questions,
        )

    # ── Private: targeted repair ──────────────────────────────────────────

    async def _repair(
        self,
        paper: PaperOutput,
        errors: List[str],
        section_slots: Dict[str, List[QuestionSlot]],
        ordered_sections: List[str],
        index_key: str,
        subject: str,
    ) -> PaperOutput:
        """
        Identify broken sections from validation errors and regenerate
        only those — not the full paper.
        """
        broken = {
            name
            for err in errors
            for name in ordered_sections
            if f"Section {name}" in err or f"section {name}" in err
        }

        if not broken:
            logger.info("No specific sections identified for repair — returning as-is.")
            return paper

        logger.info(f"Repairing sections: {sorted(broken)}")
        repaired = list(paper.sections)

        for i, section in enumerate(repaired):
            if section.section in broken and section.section in section_slots:
                logger.info(f"  Regenerating section {section.section}…")
                repaired[i] = await self._generate_section(
                    section_name=section.section,
                    slots=section_slots[section.section],
                    index_key=index_key,
                    subject=subject,
                )

        return paper.model_copy(update={"sections": repaired})

    # ── Private: helpers ──────────────────────────────────────────────────

    async def _resolve_pattern(
        self,
        manual: Optional[ManualPattern],
        pdf_path: Optional[Path],
    ) -> PaperPattern:
        """Resolve the paper pattern from manual spec, PDF, or default."""
        if manual and manual.question_structure:
            return PaperPattern(
                total_marks=manual.total_marks,
                instructions=manual.instructions or _DEFAULT_INSTRUCTIONS,
                question_structure=manual.question_structure,
            )

        if pdf_path:
            return await extract_pattern(
                pdf_path=pdf_path,
                client=self._client,
                settings=self._settings,
            )

        logger.info("No pattern provided — using default paper structure.")
        return PaperPattern(
            total_marks=_DEFAULT_TOTAL_MARKS,
            instructions=_DEFAULT_INSTRUCTIONS,
            question_structure=_DEFAULT_QUESTION_STRUCTURE,
        )

    def _load_syllabus_text(self, paths: List[Path]) -> str:
        """
        Load and concatenate text from syllabus files up to a token budget.
        """
        max_tokens = self._settings.SYLLABUS_MAX_TOKENS
        parts: List[str] = []
        used = 0

        for path in paths:
            try:
                text = load_document(path, enable_ocr=self._settings.ENABLE_OCR)
            except Exception as exc:
                logger.warning(f"Could not load {path.name} for topic extraction: {exc}")
                continue

            tokens = encode(text)
            remaining = max_tokens - used
            if remaining <= 0:
                break
            if len(tokens) > remaining:
                text = decode(tokens[:remaining])

            parts.append(text)
            used += min(len(tokens), remaining)

        return "\n\n".join(parts)