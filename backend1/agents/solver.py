# agents/solver.py
"""
Production-grade paper generation orchestrator.

Replaces one-shot agent generation with:
  1. Topic extraction from syllabus
  2. Deterministic slot distribution (topic × bloom × marks per question)
  3. Per-question multi-query retrieval
  4. Per-question context-injected generation
  5. Parallel section generation with sequential intra-section (for dedup)
  6. Validation + targeted retry on structural failures
"""

import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from agents.rag.loaders import load_document_from_path
from agents.tools import extract_paper_pattern_tool
import tiktoken
from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError
from agents.rag_pipeline import RAGPipeline, count_tokens
from agents.tools import (
    TopicTree,
    extract_topics_from_syllabus,
    generate_retrieval_queries,
    generate_single_question,
    validate_paper_output,
)
from settings import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Shared async OpenAI client
# ─────────────────────────────────────────────
_async_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# ─────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────

class Question(BaseModel):
    text: str
    marks: int
    blooms_taxonomy_level: str
    topic: str


class Section(BaseModel):
    section: str
    question_type: str
    questions: List[Question]


class PaperOutput(BaseModel):
    organization: str = ""
    program: str = ""
    course: str = ""
    exam_name: str = ""
    exam_date: str = ""
    subject: str
    total_marks: int
    instructions: List[str] = []
    sections: List[Section]


class ManualPattern(BaseModel):
    total_marks: int
    instructions: Optional[List[str]] = None
    question_structure: Optional[List[dict]] = None


class PaperSpecification(BaseModel):
    subject: str
    syllabus_files: List[str]                   # local file paths
    pattern_file_path: Optional[str] = None     # PDF pattern file (optional)
    manual_pattern: Optional[ManualPattern] = None
    difficulty_level: Optional[str] = "Mixed"

    # Paper metadata
    organization: Optional[str] = None
    program: Optional[str] = None
    course: Optional[str] = None
    exam_name: Optional[str] = None
    exam_date: Optional[str] = None


# ─────────────────────────────────────────────
# Slot model (internal planning unit)
# ─────────────────────────────────────────────

class QuestionSlot(BaseModel):
    """
    A single planned question slot.
    Fully specifies what the question generator should produce.
    """
    section: str
    slot_index: int            # position within section (0-indexed)
    topic: str
    subtopic: str
    bloom_level: str
    marks: int
    question_type: str
    difficulty: str


# ─────────────────────────────────────────────
# Bloom level mapping
# ─────────────────────────────────────────────

_BLOOM_MAP: Dict[str, List[str]] = {
    "Easy":   ["Remember", "Understand"],
    "Medium": ["Apply", "Analyze"],
    "Hard":   ["Evaluate", "Create"],
    "Mixed":  ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
}


# ─────────────────────────────────────────────
# Topic distribution
# ─────────────────────────────────────────────

def distribute_topics(
    topic_tree: TopicTree,
    question_structure: List[dict],
    difficulty: str = "Mixed",
    seed: int = 42,
) -> List[QuestionSlot]:
    """
    Deterministically distributes topics across question slots.

    Algorithm:
    - Flatten all topics with weights
    - Weighted sample (with replacement, fixed seed) for total slot count
    - Assign bloom levels from the topic's bloom_affinity filtered by difficulty
    - Build QuestionSlot for each position in each section

    Returns: ordered list of QuestionSlot
    """
    rng = random.Random(seed)
    bloom_pool = _BLOOM_MAP.get(difficulty, _BLOOM_MAP["Mixed"])

    # Flatten topics
    flat_topics = []
    for unit in topic_tree.units:
        for topic in unit.topics:
            flat_topics.append({
                "topic": topic.name,
                "subtopics": topic.subtopics or [topic.name],
                "weight": topic.estimated_weight,
                "bloom_affinity": topic.bloom_affinity or bloom_pool,
            })

    if not flat_topics:
        # Fallback: single generic topic
        flat_topics = [{
            "topic": "Core Concepts",
            "subtopics": ["Fundamentals", "Applications"],
            "weight": 1,
            "bloom_affinity": bloom_pool,
        }]

    total_slots = sum(s.get("question_count", 1) for s in question_structure)
    weights = [t["weight"] for t in flat_topics]

    # Weighted sampling — deterministic
    selected_topics = rng.choices(flat_topics, weights=weights, k=total_slots)

    slots: List[QuestionSlot] = []
    topic_iter = iter(selected_topics)

    for section_def in question_structure:
        section_name = section_def.get("section", "A")
        q_count = section_def.get("question_count", 1)
        marks_each = section_def.get("marks_each", 5)
        question_type = section_def.get("question_type", "General")

        for i in range(q_count):
            t = next(topic_iter)

            # Pick subtopic — cycle to ensure variety within section
            subtopic = t["subtopics"][i % len(t["subtopics"])]

            # Pick bloom level: prefer topic's affinity, filtered by difficulty
            eligible_bloom = [b for b in t["bloom_affinity"] if b in bloom_pool]
            if not eligible_bloom:
                eligible_bloom = bloom_pool
            bloom_level = rng.choice(eligible_bloom)

            slots.append(QuestionSlot(
                section=section_name,
                slot_index=i,
                topic=t["topic"],
                subtopic=subtopic,
                bloom_level=bloom_level,
                marks=marks_each,
                question_type=question_type,
                difficulty=difficulty,
            ))

    logger.info(f"📋 Distributed {len(slots)} question slots across {len(question_structure)} sections")
    return slots


# ─────────────────────────────────────────────
# Syllabus text extraction
# ─────────────────────────────────────────────

def extract_syllabus_text(file_paths: List[str], max_tokens: int = 6000) -> str:
    """
    Extract text from syllabus files for topic extraction.
    Respects a token budget across all files.
    """
    enc = tiktoken.get_encoding("cl100k_base")

    parts = []
    used = 0

    for path in file_paths:
        try:
            text = load_document_from_path(path)
        except Exception as e:
            logger.warning(f"Failed to read {path}: {e}")
            continue

        tokens = enc.encode(text)
        remaining = max_tokens - used
        if remaining <= 0:
            break
        if len(tokens) > remaining:
            text = enc.decode(tokens[:remaining])
        parts.append(text)
        used += min(len(tokens), remaining)

    return "\n\n".join(parts)


# ─────────────────────────────────────────────
# Section generator
# ─────────────────────────────────────────────

async def _generate_section(
    section_name: str,
    slots: List[QuestionSlot],
    retriever: RAGPipeline,
    subject: str,
    question_model: str,
) -> Section:
    """
    Generates all questions for a single section.
    Runs sequentially within section to allow dedup via previous_questions.
    """
    questions = []
    previous_q_texts: List[str] = []

    for slot in slots:
        # Step 1: Generate targeted retrieval queries for this slot
        queries = await generate_retrieval_queries(
            topic=slot.topic,
            subtopic=slot.subtopic,
            question_type=slot.question_type,
            bloom_level=slot.bloom_level,
        )

        # Step 2: Multi-query hybrid retrieval
        chunks = await retriever.multi_query_retrieve(
            queries=queries,
            k=10,
            rerank_top_n=4,
            max_context_tokens=1800,
        )

        # Step 3: Build context string
        context = retriever.build_context_string(chunks) if chunks else f"Topic: {slot.topic} — {slot.subtopic}"

        # Step 4: Generate question with dedup context
        question = await generate_single_question(
            context=context,
            subject=subject,
            topic=slot.topic,
            subtopic=slot.subtopic,
            question_type=slot.question_type,
            bloom_level=slot.bloom_level,
            marks=slot.marks,
            difficulty=slot.difficulty,
            previous_questions=previous_q_texts,
            model=question_model,
        )

        # Convert to solver's Question model (from tools.Question → solver.Question)
        q_obj = Question(
            text=question.text,
            marks=question.marks,
            blooms_taxonomy_level=question.blooms_taxonomy_level,
            topic=question.topic,
        )
        questions.append(q_obj)
        previous_q_texts.append(question.text)

        logger.info(
            f"  ✅ Section {section_name} | Q{slot.slot_index + 1} | "
            f"{slot.topic} [{slot.bloom_level}] | {slot.marks}m"
        )

    return Section(
        section=section_name,
        question_type=slots[0].question_type if slots else "General",
        questions=questions,
    )


# ─────────────────────────────────────────────
# Main pipeline: create_and_run_agent
# (kept as drop-in replacement for existing callers)
# ─────────────────────────────────────────────

async def create_and_run_agent(spec: PaperSpecification) -> Dict[str, Any]:
    """
    Main entry point — generates a full question paper.

    Flow:
    1. Ensure syllabus files are indexed (cached by file hash — never re-indexed per request)
    2. Extract topic tree from syllabus text
    3. Distribute topics into QuestionSlots deterministically
    4. Generate sections in parallel (each section runs questions sequentially for dedup)
    5. Assemble PaperOutput
    6. Validate structure and marks
    7. Retry any sections with structural errors (targeted, not full regen)

    Returns: dict matching PaperOutput schema
    """
    logger.info(f"🚀 Starting paper generation for: {spec.subject}")

    # ── 1. Resolve question structure ──
    question_structure = []
    if spec.manual_pattern and spec.manual_pattern.question_structure:
        question_structure = spec.manual_pattern.question_structure
    elif spec.pattern_file_path:
        # Import here to avoid circular (extract_paper_pattern_tool is agno @tool)
        pattern_data = await extract_paper_pattern_tool.run_async(file_path=spec.pattern_file_path)
        question_structure = pattern_data.get("question_structure", [])
        if not spec.manual_pattern:
            spec.manual_pattern = ManualPattern(
                total_marks=pattern_data.get("total_marks", 100),
                instructions=pattern_data.get("instructions", []),
                question_structure=question_structure,
            )
    else:
        # Default pattern
        question_structure = [
            {"section": "A", "question_count": 5, "marks_each": 4, "question_type": "Short Answer"},
            {"section": "B", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
            {"section": "C", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
        ]
        spec.manual_pattern = ManualPattern(
            total_marks=80,
            instructions=["Answer all questions."],
            question_structure=question_structure,
        )

    total_marks = spec.manual_pattern.total_marks if spec.manual_pattern else 100
    instructions = spec.manual_pattern.instructions or [] if spec.manual_pattern else []

    # ── 2. Build / load index (cached) ──
    pipeline = RAGPipeline(
        base_index_dir=settings.RAG_INDEX_DIR,
        openai_api_key=settings.OPENAI_API_KEY,
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        cohere_api_key=getattr(settings, "COHERE_API_KEY", None),
        enrich_chunks=True,
    )
    try:
        await pipeline.ensure_indexed(spec.syllabus_files, force_reindex=False)
        logger.info("✅ Index ready")
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return {"error": "Indexing failed", "detail": str(e)}

    # ── 3. Extract topic tree from syllabus ──
    syllabus_text = extract_syllabus_text(spec.syllabus_files)
    topic_tree = await extract_topics_from_syllabus(
        syllabus_text=syllabus_text,
        subject_hint=spec.subject,
    )

    # ── 4. Distribute topics into slots ──
    difficulty = spec.difficulty_level or "Mixed"
    slots = distribute_topics(topic_tree, question_structure, difficulty=difficulty)

    # ── 5. Group slots by section ──
    section_slots: Dict[str, List[QuestionSlot]] = {}
    for slot in slots:
        section_slots.setdefault(slot.section, []).append(slot)

    # Preserve section order from question_structure
    ordered_section_names = [s["section"] for s in question_structure]

    # ── 6. Generate sections in parallel ──
    logger.info(f"⚙️  Generating {len(section_slots)} sections in parallel...")
    model = getattr(settings, "GENERATION_MODEL_NAME", "gpt-4o-mini")

    section_tasks = [
        _generate_section(
            section_name=name,
            slots=section_slots.get(name, []),
            retriever=pipeline,
            subject=spec.subject,
            question_model=model,
        )
        for name in ordered_section_names
        if name in section_slots
    ]
    sections: List[Section] = await asyncio.gather(*section_tasks)

    # ── 7. Assemble paper ──
    paper = PaperOutput(
        organization=spec.organization or "",
        program=spec.program or "",
        course=spec.course or "",
        exam_name=spec.exam_name or "",
        exam_date=spec.exam_date or "",
        subject=spec.subject,
        total_marks=total_marks,
        instructions=instructions,
        sections=list(sections),
    )

    # ── 8. Validate ──
    paper_dict = paper.model_dump()
    validation_errors = validate_paper_output(
        sections=paper_dict["sections"],
        question_structure=question_structure,
        expected_total_marks=total_marks,
    )

    if validation_errors:
        logger.warning(f"⚠️ Validation issues ({len(validation_errors)}):")
        for err in validation_errors:
            logger.warning(f"   - {err}")

        # Targeted retry: regenerate only structurally broken sections
        paper = await _repair_paper(
            paper=paper,
            errors=validation_errors,
            section_slots=section_slots,
            retriever=pipeline,
            subject=spec.subject,
            question_model=model,
            ordered_section_names=ordered_section_names,
        )
        paper_dict = paper.model_dump()

    logger.info(f"🎉 Paper generation complete: {len(paper.sections)} sections")
    return paper_dict


# ─────────────────────────────────────────────
# Repair logic
# ─────────────────────────────────────────────

async def _repair_paper(
    paper: PaperOutput,
    errors: List[str],
    section_slots: Dict[str, List[QuestionSlot]],
    retriever: RAGPipeline,
    subject: str,
    question_model: str,
    ordered_section_names: List[str],
) -> PaperOutput:
    """
    Identifies which sections have structural errors and regenerates them.
    Only regenerates affected sections — not the full paper.
    """
    # Parse which sections need repair
    broken_sections = set()
    for err in errors:
        for name in ordered_section_names:
            if f"Section {name}" in err or f"section {name}" in err:
                broken_sections.add(name)

    if not broken_sections:
        logger.info("No specific section identified for repair — skipping targeted retry.")
        return paper

    logger.info(f"🔧 Repairing sections: {broken_sections}")

    repaired_sections = list(paper.sections)
    for i, section in enumerate(repaired_sections):
        if section.section in broken_sections and section.section in section_slots:
            logger.info(f"  🔄 Regenerating section {section.section}...")
            new_section = await _generate_section(
                section_name=section.section,
                slots=section_slots[section.section],
                retriever=retriever,
                subject=subject,
                question_model=question_model,
            )
            repaired_sections[i] = new_section

    return PaperOutput(
        organization=paper.organization,
        program=paper.program,
        course=paper.course,
        exam_name=paper.exam_name,
        exam_date=paper.exam_date,
        subject=paper.subject,
        total_marks=paper.total_marks,
        instructions=paper.instructions,
        sections=repaired_sections,
    )