# app/generation/question_generator.py
"""
Single question generator.

Takes a retrieved context string and a fully-specified question slot,
returns a validated Question. Retries with increasing temperature on
JSON/validation failure. Falls back to a safe placeholder question
if all retries are exhausted — the pipeline never crashes over a single
bad LLM response.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import List, Optional

from openai import AsyncOpenAI

from  app.core.config import Settings
from  app.schemas.paper import Question

logger = logging.getLogger(__name__)

_PROMPT = """\
You are a senior university examiner. Generate exactly ONE {question_type} question.

Syllabus Context (use this for factual grounding — do not invent content):
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
1. The question must be answerable from the syllabus context above.
2. It must clearly test the specified Bloom's level.
3. It must not overlap semantically with any previously asked question.
4. Long Answer (8-15 marks): require detailed explanation, derivation, or design.
5. Short Answer (2-6 marks): ask for definitions, differences, or brief descriptions.
6. MCQ: provide 4 options (A–D) with exactly one correct answer; embed options in "text".

Return ONLY valid JSON — no markdown, no commentary:
{{
  "text": "<full question text>",
  "marks": {marks},
  "blooms_taxonomy_level": "{bloom_level}",
  "topic": "{topic}"
}}
"""


async def generate_question(
    context: str,
    subject: str,
    topic: str,
    subtopic: str,
    question_type: str,
    bloom_level: str,
    marks: int,
    difficulty: str = "Medium",
    previous_questions: Optional[List[str]] = None,
    client: AsyncOpenAI = None,     # type: ignore[assignment]
    settings: Settings = None,      # type: ignore[assignment]
) -> Question:
    """
    Generate a single validated question with retry logic.

    Args:
        context:            Retrieved syllabus chunks as a formatted string.
        subject:            Course/subject name.
        topic:              Topic from the syllabus TopicTree.
        subtopic:           Specific subtopic within the topic.
        question_type:      "Short Answer" | "Long Answer" | "MCQ"
        bloom_level:        Bloom's taxonomy level string.
        marks:              Marks allocated (enforced in output regardless of LLM).
        difficulty:         "Easy" | "Medium" | "Hard" | "Mixed"
        previous_questions: Texts of already-generated questions for dedup.
        client:             Shared AsyncOpenAI client.
        settings:           Application settings.

    Returns:
        Question Pydantic model.
    """
    previous_questions = previous_questions or []
    max_retries = settings.MAX_RETRIES_QUESTION if settings else 3
    model = settings.GENERATION_MODEL if settings else "gpt-4o-mini"

    prev_text = (
        "\n".join(f"  - {q}" for q in previous_questions[-8:])
        if previous_questions
        else "  (none — this is the first question)"
    )

    prompt = _PROMPT.format(
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

    last_exc: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        # Slightly increase temperature on each retry for more variety
        temperature = round(0.4 + (attempt - 1) * 0.15, 2)
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=600,
            )
            raw = resp.choices[0].message.content
            data = json.loads(raw)

            # Force marks to match the slot specification regardless of what
            # the LLM outputs — this keeps the mark total deterministic.
            data["marks"] = marks

            question = Question(**data)
            logger.debug(
                f"Question generated [attempt {attempt}, temp={temperature}]: "
                f"{topic} / {bloom_level}"
            )
            return question

        except Exception as exc:
            last_exc = exc
            logger.warning(
                f"Question generation attempt {attempt}/{max_retries} failed "
                f"(topic={topic}, bloom={bloom_level}): {exc}"
            )
            if attempt < max_retries:
                await asyncio.sleep(0.5 * attempt)

    # All retries exhausted — return a safe, grammatically correct placeholder
    logger.error(
        f"All {max_retries} attempts failed for topic='{topic}'. "
        f"Returning fallback question. Last error: {last_exc}"
    )
    return Question(
        text=(
            f"Explain the concept of {subtopic} in the context of {topic}. "
            f"Provide a detailed explanation with relevant examples."
        ),
        marks=marks,
        blooms_taxonomy_level=bloom_level,
        topic=topic,
    )