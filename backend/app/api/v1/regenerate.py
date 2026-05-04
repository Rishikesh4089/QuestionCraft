# app/api/v1/regenerate.py
"""
Regeneration endpoints.

POST /regenerate-question/  — Regenerate a single question
POST /regenerate-section/   — Regenerate an entire section

Both endpoints require an `index_key` returned from /generate-paper/.
The syllabus does NOT need to be re-uploaded — the index is already
on disk from the original generation request.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from  app.core.config import get_settings
from  app.core.dependencies import RAGPipelineDep
from  app.core.exceptions import IndexNotFoundError
from  app.schemas.requests import RegenerateQuestionRequest, RegenerateSectionRequest
from  app.schemas.responses import RegenerateQuestionResponse, RegenerateSectionResponse
from  app.services.paper_service import PaperService

router = APIRouter(tags=["Regeneration"])
logger = logging.getLogger(__name__)


@router.post(
    "/regenerate-question/",
    response_model=RegenerateQuestionResponse,
    summary="Regenerate a single question",
)
async def regenerate_question(
    payload: RegenerateQuestionRequest,
    rag: RAGPipelineDep,
):
    """
    Regenerate one question for a given topic and slot specification.

    Requires `index_key` from the original /generate-paper/ response.
    Pass `previous_questions` (list of already-generated question texts in this
    section) to prevent the regenerated question from repeating them.
    """
    if not payload.index_key:
        raise HTTPException(
            status_code=400,
            detail="index_key is required. Use the value returned by /generate-paper/.",
        )

    settings = get_settings()
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    service = PaperService(rag=rag, client=client, settings=settings)

    try:
        question = await service.regenerate_question(
            index_key=payload.index_key,
            subject=payload.subject,
            topic=payload.topic,
            subtopic=payload.subtopic or payload.topic,
            question_type=payload.question_type,
            bloom_level=payload.bloom_level,
            marks=payload.marks,
            difficulty=payload.difficulty_level,
            previous_questions=payload.previous_questions,
        )
    except IndexNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return RegenerateQuestionResponse(success=True, new_question=question.model_dump())


@router.post(
    "/regenerate-section/",
    response_model=RegenerateSectionResponse,
    summary="Regenerate an entire section",
)
async def regenerate_section(
    payload: RegenerateSectionRequest,
    rag: RAGPipelineDep,
):
    """
    Regenerate all questions in a section.

    The topics and Bloom's levels are inferred from the existing questions
    you pass in `questions`. Each question is regenerated fresh with
    deduplication against the others in that section.

    Requires `index_key` from the original /generate-paper/ response.
    """
    if not payload.index_key:
        raise HTTPException(
            status_code=400,
            detail="index_key is required. Use the value returned by /generate-paper/.",
        )

    settings = get_settings()
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    service = PaperService(rag=rag, client=client, settings=settings)

    try:
        section = await service.regenerate_section(
            index_key=payload.index_key,
            subject=payload.subject,
            section_name=payload.section,
            question_type=payload.question_type,
            existing_questions=payload.questions,
            marks_each=payload.marks_each,
            difficulty=payload.difficulty_level,
        )
    except IndexNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return RegenerateSectionResponse(section=section.model_dump())