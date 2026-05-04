# app/generation/query_generator.py
"""
Generate targeted retrieval queries for a question slot.

Three queries per slot — each targeting a different angle — dramatically
improves recall over a single query, especially for syllabus content
that's scattered across slides and notes.
"""
from __future__ import annotations

import logging
from typing import List

from openai import AsyncOpenAI

from  app.core.config import Settings

logger = logging.getLogger(__name__)

_PROMPT = """\
Generate exactly 3 short, distinct search queries to retrieve relevant syllabus \
content for generating a {question_type} question.

Question slot details:
- Topic: {topic}
- Subtopic: {subtopic}
- Bloom's level: {bloom_level}

Each query must target a different angle:
1. Conceptual definition / what it is
2. Mechanism / how it works / underlying process
3. Application / real-world example / use case

Return ONLY a JSON array of exactly 3 strings. No markdown, no extra text.
Example: ["query one", "query two", "query three"]
"""


def _fallback_queries(topic: str, subtopic: str) -> List[str]:
    return [
        f"{topic} {subtopic} definition concept",
        f"{topic} {subtopic} how it works mechanism",
        f"{topic} {subtopic} application example",
    ]


async def generate_queries(
    topic: str,
    subtopic: str,
    question_type: str,
    bloom_level: str,
    client: AsyncOpenAI,
    settings: Settings,
) -> List[str]:
    """
    Generate 3 retrieval queries for a question slot.

    Always returns a list of at least 3 strings — falls back gracefully
    on any API or parse failure.
    """
    import json

    prompt = _PROMPT.format(
        topic=topic,
        subtopic=subtopic,
        question_type=question_type,
        bloom_level=bloom_level,
    )
    model = settings.ENRICHMENT_MODEL  # cheap model is fine here

    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()

        # Strip markdown fences if the model ignores instructions
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        queries = json.loads(raw)
        if isinstance(queries, list) and len(queries) >= 2:
            valid = [str(q).strip() for q in queries[:3] if str(q).strip()]
            if valid:
                return valid
    except Exception as exc:
        logger.warning(f"Query generation failed for '{topic}/{subtopic}': {exc}")

    return _fallback_queries(topic, subtopic)