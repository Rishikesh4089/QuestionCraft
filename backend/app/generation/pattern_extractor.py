# app/generation/pattern_extractor.py
"""
Extract PaperPattern (marks, instructions, section structure) from a PDF.

Used when the caller uploads a reference question paper for the system
to mimic its structure, rather than specifying a manual pattern.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from openai import AsyncOpenAI

from  app.core.config import Settings
from  app.core.exceptions import PatternExtractionError
from  app.rag.loaders.pdf import PDFLoader
from  app.schemas.pattern import PaperPattern

logger = logging.getLogger(__name__)

_PROMPT = """\
You are an expert at parsing university question paper formats.
Analyze the question paper text below and extract:
1. Total marks
2. Student instructions (as a list of strings)
3. Section-wise question structure

Return ONLY valid JSON matching this exact schema — no markdown, no preamble:
{{
  "total_marks": 100,
  "instructions": ["Instruction 1", "Instruction 2"],
  "question_structure": [
    {{"section": "A", "question_count": 5, "marks_each": 4, "question_type": "Short Answer"}},
    {{"section": "B", "question_count": 3, "marks_each": 10, "question_type": "Long Answer"}}
  ]
}}

Question Paper Text:
---
{text}
---
"""

_DEFAULT_PATTERN = PaperPattern(
    total_marks=100,
    instructions=[
        "Answer all questions from Section A.",
        "Answer any two from each of the remaining sections.",
        "Figures to the right indicate full marks.",
        "Assume suitable data wherever required.",
    ],
    question_structure=[
        {"section": "A", "question_count": 5, "marks_each": 4,  "question_type": "Short Answer"},
        {"section": "B", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
        {"section": "C", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
        {"section": "D", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
        {"section": "E", "question_count": 2, "marks_each": 10, "question_type": "Long Answer"},
    ],
)


async def extract_pattern(
    pdf_path: Path,
    client: AsyncOpenAI,
    settings: Settings,
) -> PaperPattern:
    """
    Extract a PaperPattern from a reference question paper PDF.

    Steps:
      1. Extract text via PDFLoader (OCR if needed)
      2. Send to LLM for structured extraction
      3. Validate and return a PaperPattern model

    Returns the default pattern on any unrecoverable failure.
    """
    loader = PDFLoader(enable_ocr=settings.ENABLE_OCR)

    try:
        text = loader.load(pdf_path)
    except Exception as exc:
        logger.warning(f"PDF load failed for pattern extraction: {exc}. Using default pattern.")
        return _DEFAULT_PATTERN

    if not text.strip():
        logger.warning("Pattern PDF produced no text. Using default pattern.")
        return _DEFAULT_PATTERN

    prompt = _PROMPT.format(text=text[:4000])

    try:
        resp = await client.chat.completions.create(
            model=settings.GENERATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        pattern = PaperPattern(**data)
        logger.info(
            f"Pattern extracted: {pattern.total_marks} marks, "
            f"{len(pattern.question_structure)} sections"
        )
        return pattern
    except Exception as exc:
        logger.error(f"Pattern extraction LLM call failed: {exc}. Using default pattern.")
        return _DEFAULT_PATTERN