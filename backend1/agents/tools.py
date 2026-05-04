# agents/tools.py
"""
Agent tools — clean, non-recursive implementations.

Tools in this file:
  1. extract_paper_pattern_tool   — PDF → PaperPattern JSON (kept as agno @tool for agent use)
  2. generate_retrieval_queries   — question slot → 3 targeted retrieval queries (plain async fn)
  3. generate_single_question     — single question generator, context-injected (plain async fn)
  4. extract_topics_from_syllabus — syllabus text → structured TopicTree (plain async fn)

NOTE: generate_single_question and generate_retrieval_queries are NOT @tool decorated.
They are plain async functions called directly from paper_assembler (solver.py).
Only extract_paper_pattern_tool is an agno @tool, used by the pattern-extraction agent.
"""

import json
import logging
import asyncio
from typing import List, Optional, Dict, Any
from agents.rag_pipeline import count_tokens, _enc
import pypdf
from pydantic import BaseModel, Field
from agno.tools import tool
from agno.models.openai import OpenAIChat
from openai import AsyncOpenAI

from settings import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Optional OCR imports
# ─────────────────────────────────────────────
try:
    from pdf2image import convert_from_path
    import pytesseract
    HAS_OCR = True
except ImportError:
    convert_from_path = None
    pytesseract = None
    HAS_OCR = False

# ─────────────────────────────────────────────
# Shared clients
# ─────────────────────────────────────────────
_async_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

_tool_llm = OpenAIChat(
    id=settings.GENERATION_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.0,
)


# ─────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────

class Question(BaseModel):
    text: str = Field(..., description="Full question text.")
    marks: int = Field(..., description="Marks allocated.")
    blooms_taxonomy_level: str = Field(..., description="Bloom's taxonomy level.")
    topic: str = Field(..., description="Topic from the syllabus.")


class PaperPattern(BaseModel):
    total_marks: int = Field(..., description="Total marks for the paper.")
    instructions: List[str] = Field(default_factory=list)
    question_structure: List[dict] = Field(
        ..., description="List of section definitions."
    )


class TopicEntry(BaseModel):
    name: str
    subtopics: List[str] = Field(default_factory=list)
    estimated_weight: int = Field(default=3, ge=1, le=5)
    bloom_affinity: List[str] = Field(
        default_factory=lambda: ["Remember", "Understand", "Apply"]
    )


class UnitEntry(BaseModel):
    unit_number: int
    unit_name: str
    topics: List[TopicEntry]


class TopicTree(BaseModel):
    subject: str
    units: List[UnitEntry]


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _clean_json_response(text: str) -> str:
    """Strip markdown code fences from LLM JSON response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _recover_json(text: str) -> Any:
    """Try full parse, then substring recovery."""
    cleaned = _clean_json_response(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(cleaned[start:end])
        start = cleaned.find("[")
        end = cleaned.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(cleaned[start:end])
        raise


# ─────────────────────────────────────────────
# Tool 1: Extract Paper Pattern (agno @tool)
# ─────────────────────────────────────────────

@tool
async def extract_paper_pattern_tool(file_path: str) -> dict:
    """
    Reads a question paper PDF and extracts its structure:
    total marks, instructions, and section-wise question breakdown.
    Includes OCR fallback for scanned PDFs.
    Returns a dict matching PaperPattern schema.
    """
    logger.info(f"📄 Extracting paper pattern from: {file_path}")
    text_content = ""

    # Step 1: PyPDF text extraction
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                text_content += txt + "\n"
    except Exception as e:
        logger.warning(f"PyPDF extraction failed: {e}")

    # Step 2: OCR fallback
    if not text_content.strip() and HAS_OCR:
        logger.info("🔍 Running OCR fallback...")
        try:
            images = convert_from_path(file_path)
            for img in images:
                text_content += pytesseract.image_to_string(img)
        except Exception as e:
            logger.warning(f"OCR fallback failed: {e}")

    if not text_content.strip():
        logger.error("No readable text in PDF. Returning default pattern.")
        return _default_pattern()

    # Step 3: LLM extraction
    prompt = f"""
You are an expert at parsing university question paper formats.
Analyze the question paper text below and extract:
1. Total marks
2. Student instructions (as a list of strings)
3. Section-wise structure

Return ONLY valid JSON matching this exact schema:
{{
  "total_marks": 100,
  "instructions": ["Instruction 1", "Instruction 2"],
  "question_structure": [
    {{"section": "A", "question_count": 5, "marks_each": 4, "question_type": "Short Answer"}},
    {{"section": "B", "question_count": 3, "marks_each": 10, "question_type": "Long Answer"}}
  ]
}}

Do NOT include commentary or markdown. Only JSON.

Question Paper Text:
---
{text_content[:4000]}
---
"""

    try:
        resp = await _async_openai.chat.completions.create(
            model=settings.GENERATION_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        pattern = PaperPattern(**data)
        logger.info(f"✅ Pattern extracted: {pattern.total_marks} marks, {len(pattern.question_structure)} sections")
        return pattern.model_dump()
    except Exception as e:
        logger.error(f"Pattern extraction LLM call failed: {e}")
        return _default_pattern()


def _default_pattern() -> dict:
    return PaperPattern(
        total_marks=100,
        instructions=[
            "Answer all questions from Section A.",
            "Answer any two from each of the remaining sections.",
            "Figures to the right indicate full marks.",
            "Assume suitable data wherever required.",
        ],
        question_structure=[
            {"section": "A", "question_count": 5, "marks_each": 4, "question_type": "Short Answer"},
            {"section": "B", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
            {"section": "C", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
            {"section": "D", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
            {"section": "E", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
        ],
    ).model_dump()


# ─────────────────────────────────────────────
# Tool 2: Extract Topics from Syllabus
# (plain async fn — called from solver, not agent)
# ─────────────────────────────────────────────

_TOPIC_EXTRACT_PROMPT = """
You are analyzing a university course syllabus. Extract all topics in a structured JSON format.

Rules:
- Identify each unit/module and its constituent topics
- For each topic, list 2-5 subtopics
- Assign estimated_weight (1-5) based on coverage in the syllabus
- Assign bloom_affinity: which Bloom's levels this topic typically tests

Return ONLY valid JSON. No preamble, no markdown.

Schema:
{{
  "subject": "<subject name>",
  "units": [
    {{
      "unit_number": 1,
      "unit_name": "<unit name>",
      "topics": [
        {{
          "name": "<topic name>",
          "subtopics": ["<subtopic1>", "<subtopic2>"],
          "estimated_weight": 3,
          "bloom_affinity": ["Remember", "Understand", "Apply"]
        }}
      ]
    }}
  ]
}}

Syllabus text:
---
{syllabus_text}
---
"""

async def extract_topics_from_syllabus(
    syllabus_text: str,
    subject_hint: str = "",
    model: str = "gpt-4o-mini",
) -> TopicTree:
    """
    Extracts a structured topic tree from syllabus text.
    Uses first 5000 tokens of syllabus for efficiency.

    Returns: TopicTree Pydantic model
    """
    

    # Truncate to ~5000 tokens
    tokens = _enc.encode(syllabus_text)
    if len(tokens) > 5000:
        syllabus_text = _enc.decode(tokens[:5000])

    prompt = _TOPIC_EXTRACT_PROMPT.format(syllabus_text=syllabus_text)
    if subject_hint:
        prompt += f"\n\nSubject hint: {subject_hint}"

    try:
        resp = await _async_openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=2000,
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        topic_tree = TopicTree(**data)
        logger.info(
            f"✅ Topic extraction: {len(topic_tree.units)} units, "
            f"{sum(len(u.topics) for u in topic_tree.units)} topics"
        )
        return topic_tree
    except Exception as e:
        logger.error(f"Topic extraction failed: {e}")
        # Return minimal fallback
        return TopicTree(
            subject=subject_hint or "Unknown Subject",
            units=[
                UnitEntry(
                    unit_number=1,
                    unit_name="General Content",
                    topics=[
                        TopicEntry(
                            name="Core Concepts",
                            subtopics=["Fundamentals", "Applications", "Examples"],
                            estimated_weight=3,
                            bloom_affinity=["Remember", "Understand", "Apply"],
                        )
                    ],
                )
            ],
        )


# ─────────────────────────────────────────────
# Tool 3: Generate Retrieval Queries
# (plain async fn)
# ─────────────────────────────────────────────

_QUERY_GEN_PROMPT = """
Generate exactly 3 short, distinct search queries to retrieve relevant syllabus content for generating a question.

Question slot details:
- Topic: {topic}
- Subtopic: {subtopic}
- Question type: {question_type}
- Bloom's level: {bloom_level}

Each query must target a different angle:
1. Conceptual definition / what is it
2. Mechanism / how it works / process
3. Application / example / use case

Return ONLY a JSON array of exactly 3 strings.
Example: ["query one", "query two", "query three"]
"""

async def generate_retrieval_queries(
    topic: str,
    subtopic: str,
    question_type: str,
    bloom_level: str,
    model: str = "gpt-4o-mini",
) -> List[str]:
    """
    Generates 3 targeted retrieval queries for a question slot.
    Falls back to a simple query list if the LLM call fails.
    """
    prompt = _QUERY_GEN_PROMPT.format(
        topic=topic,
        subtopic=subtopic,
        question_type=question_type,
        bloom_level=bloom_level,
    )

    try:
        resp = await _async_openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()
        queries = _recover_json(raw)
        if isinstance(queries, list) and len(queries) >= 2:
            return [str(q) for q in queries[:3]]
    except Exception as e:
        logger.warning(f"Query generation failed: {e}")

    # Fallback: construct queries manually
    return [
        f"{topic} {subtopic} definition",
        f"{topic} {subtopic} mechanism process",
        f"{topic} {subtopic} application example",
    ]


# ─────────────────────────────────────────────
# Tool 4: Generate Single Question
# (plain async fn — the core generation unit)
# ─────────────────────────────────────────────

_QUESTION_GEN_PROMPT = """
You are a senior university examiner. Generate exactly ONE {question_type} question.

Syllabus Context (use for factual grounding):
{context}

Question Requirements:
- Subject: {subject}
- Topic: {topic}
- Subtopic: {subtopic}
- Question Type: {question_type}
- Bloom's Taxonomy Level: {bloom_level}
- Marks: {marks}
- Difficulty: {difficulty}

Previously asked questions in this paper (your question MUST NOT repeat these concepts or phrasings):
{previous_questions_text}

Rules:
1. The question must be answerable from the syllabus context above
2. It must clearly test the specified Bloom's level
3. It must not overlap semantically with previous questions
4. For "Long Answer" questions: ask something that requires detailed explanation (8-15 marks)
5. For "Short Answer" questions: ask for definitions, differences, or brief explanations (2-6 marks)
6. For "MCQ": provide 4 options (A-D) with exactly one correct answer embedded in "text" field

Return ONLY valid JSON:
{{
  "text": "<full question text, including options if MCQ>",
  "marks": {marks},
  "blooms_taxonomy_level": "{bloom_level}",
  "topic": "{topic}"
}}
"""

async def generate_single_question(
    context: str,
    subject: str,
    topic: str,
    subtopic: str,
    question_type: str,
    bloom_level: str,
    marks: int,
    difficulty: str = "Medium",
    previous_questions: Optional[List[str]] = None,
    model: Optional[str] = None,
    max_retries: int = 3,
) -> Question:
    """
    Generates a single validated question.
    Retries up to max_retries times on JSON parse or validation failure.
    Returns a Question Pydantic model.
    """
    previous_questions = previous_questions or []
    model = model or settings.GENERATION_MODEL_NAME

    prev_text = (
        "\n".join(f"  - {q}" for q in previous_questions[-8:])  # last 8 to keep prompt lean
        if previous_questions
        else "  (none yet — this is the first question)"
    )

    prompt = _QUESTION_GEN_PROMPT.format(
        context=context,
        subject=subject,
        topic=topic,
        subtopic=subtopic,
        question_type=question_type,
        bloom_level=bloom_level,
        marks=marks,
        difficulty=difficulty,
        previous_questions_text=prev_text,
    )

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = await _async_openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},  # guarantees valid JSON
                temperature=0.4 + (attempt * 0.1),        # slightly more creative on retry
                max_tokens=500,
            )
            raw = resp.choices[0].message.content
            data = json.loads(raw)

            # Ensure marks field matches slot spec (LLM sometimes ignores it)
            data["marks"] = marks

            question = Question(**data)
            logger.debug(f"✅ Question generated [attempt {attempt}]: {question.topic}")
            return question

        except Exception as e:
            last_error = e
            logger.warning(f"Question generation attempt {attempt} failed: {e}")
            await asyncio.sleep(0.5 * attempt)

    # Final fallback: return a placeholder question so the pipeline doesn't crash
    logger.error(f"All {max_retries} attempts failed for topic '{topic}'. Using fallback. Last error: {last_error}")
    return Question(
        text=f"Explain the concept of {subtopic} in the context of {topic}. Provide examples where applicable.",
        marks=marks,
        blooms_taxonomy_level=bloom_level,
        topic=topic,
    )


# ─────────────────────────────────────────────
# Tool 5: Validate Paper Output
# (plain fn — called from solver after assembly)
# ─────────────────────────────────────────────

def validate_paper_output(
    sections: List[dict],
    question_structure: List[dict],
    expected_total_marks: int,
) -> List[str]:
    """
    Validates a generated paper against the expected structure.
    Returns a list of error strings (empty = valid).
    """
    errors = []

    # Check total marks
    actual_total = sum(
        q["marks"]
        for s in sections
        for q in s.get("questions", [])
    )
    if actual_total != expected_total_marks:
        errors.append(
            f"Mark total mismatch: expected {expected_total_marks}, got {actual_total}"
        )

    # Check section count
    expected_sections = {s["section"] for s in question_structure}
    actual_sections = {s["section"] for s in sections}
    missing = expected_sections - actual_sections
    if missing:
        errors.append(f"Missing sections: {missing}")

    # Check question counts per section
    for exp in question_structure:
        actual = next((s for s in sections if s["section"] == exp["section"]), None)
        if actual is None:
            continue
        actual_count = len(actual.get("questions", []))
        expected_count = exp["question_count"]
        if actual_count != expected_count:
            errors.append(
                f"Section {exp['section']}: expected {expected_count} questions, got {actual_count}"
            )

    # Check topic diversity
    all_topics = [
        q["topic"]
        for s in sections
        for q in s.get("questions", [])
    ]
    if all_topics:
        unique_ratio = len(set(all_topics)) / len(all_topics)
        if unique_ratio < 0.5:
            errors.append(
                f"Low topic diversity ({unique_ratio:.0%} unique) — paper may be repetitive"
            )

    return errors