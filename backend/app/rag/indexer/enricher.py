# app/rag/indexer/enricher.py
"""
LLM-based chunk metadata enricher.

Runs a cheap gpt-4o-mini call per chunk to tag it with:
  - topic       (3-5 words)
  - subtopic    (3-5 words)
  - content_type (definition | theory | example | formula | procedure | overview)

Enrichment is best-effort: failures fall back to empty strings and never
block index construction.

Concurrency is capped via asyncio.Semaphore to avoid overwhelming the API.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import List

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

_PROMPT = """\
Analyze this syllabus excerpt and return JSON ONLY — no markdown, no preamble.

{{
  "topic": "<main topic in 3-5 words>",
  "subtopic": "<specific subtopic in 3-5 words>",
  "content_type": "<one of: definition|theory|example|formula|procedure|overview>"
}}

Text:
{text}
"""

_FALLBACK = {"topic": "", "subtopic": "", "content_type": "general"}


async def _enrich_one(
    chunk_text: str,
    client: AsyncOpenAI,
    model: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    """Enrich a single chunk. Returns fallback dict on any failure."""
    async with semaphore:
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": _PROMPT.format(text=chunk_text[:600])}],
                response_format={"type": "json_object"},
                max_tokens=80,
                temperature=0.0,
            )
            data = json.loads(resp.choices[0].message.content)
            return {
                "topic": data.get("topic", ""),
                "subtopic": data.get("subtopic", ""),
                "content_type": data.get("content_type", "general"),
            }
        except Exception as exc:
            logger.debug(f"Chunk enrichment failed (non-critical): {exc}")
            return _FALLBACK.copy()


async def enrich_chunks(
    chunks: List[str],
    client: AsyncOpenAI,
    model: str = "gpt-4o-mini",
    concurrency: int = 20,
) -> List[dict]:
    """
    Enrich all chunks concurrently up to *concurrency* parallel calls.

    Returns a list of dicts (same length as *chunks*), each with keys:
      topic, subtopic, content_type
    """
    if not chunks:
        return []

    semaphore = asyncio.Semaphore(concurrency)
    tasks = [_enrich_one(chunk, client, model, semaphore) for chunk in chunks]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched: List[dict] = []
    for r in results:
        if isinstance(r, Exception):
            enriched.append(_FALLBACK.copy())
        else:
            enriched.append(r)  # type: ignore[arg-type]

    logger.info(f"Enriched {len(enriched)} chunks (model={model})")
    return enriched