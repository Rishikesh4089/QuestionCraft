# app/generation/topic_extractor.py
"""
Extract a structured TopicTree from raw syllabus text using an LLM.

The TopicTree drives all downstream slot distribution — every question
in the paper traces back to a topic and subtopic identified here.
"""
from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from  app.core.config import Settings
from  app.core.exceptions import TopicExtractionError
from  app.rag.indexer.chunker import decode, encode
from  app.schemas.rag import TopicTree, UnitEntry, TopicEntry

logger = logging.getLogger(__name__)

_PROMPT = """\
You are analyzing a university course syllabus. Extract all topics in a structured JSON format.

Rules:
- Identify each unit/module and its constituent topics
- For each topic, list 2-5 subtopics
- Assign estimated_weight (1-5) based on depth of coverage in the syllabus
- Assign bloom_affinity: which Bloom's levels this topic typically tests
  (choose from: Remember, Understand, Apply, Analyze, Evaluate, Create)

Return ONLY valid JSON matching this exact schema — no preamble, no markdown fences:

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

_FALLBACK_TREE = TopicTree(
    subject="Unknown Subject",
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


async def extract_topics(
    syllabus_text: str,
    subject_hint: str = "",
    client: AsyncOpenAI = None,  # type: ignore[assignment]
    settings: Settings = None,   # type: ignore[assignment]
) -> TopicTree:
    """
    Extract a TopicTree from syllabus text.

    Args:
        syllabus_text: Raw text from all syllabus documents (pre-concatenated).
        subject_hint:  Subject name to help the LLM contextualise extraction.
        client:        Shared AsyncOpenAI client.
        settings:      Application settings.

    Returns:
        TopicTree Pydantic model. Falls back to a single generic unit on failure.
    """
    # Truncate to token budget
    tokens = encode(syllabus_text)
    max_tokens = settings.TOPIC_EXTRACT_MAX_TOKENS if settings else 5000
    if len(tokens) > max_tokens:
        syllabus_text = decode(tokens[:max_tokens])
        logger.debug(f"Syllabus truncated to {max_tokens} tokens for topic extraction")

    prompt = _PROMPT.format(syllabus_text=syllabus_text)
    if subject_hint:
        prompt += f"\n\nSubject: {subject_hint}"

    model = settings.ENRICHMENT_MODEL if settings else "gpt-4o-mini"

    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=2000,
        )
        data = json.loads(resp.choices[0].message.content)
        tree = TopicTree(**data)
        total_topics = sum(len(u.topics) for u in tree.units)
        logger.info(f"Topic extraction: {len(tree.units)} units, {total_topics} topics")
        return tree
    except Exception as exc:
        logger.error(f"Topic extraction failed, using fallback: {exc}")
        fallback = _FALLBACK_TREE.model_copy(deep=True)
        fallback.subject = subject_hint or fallback.subject
        return fallback