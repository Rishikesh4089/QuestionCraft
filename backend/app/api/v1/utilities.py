# app/api/v1/utilities.py
"""
Utility endpoints.

POST /extract-pattern/  — Extract paper structure from a reference PDF
POST /index-status/     — Check if a file set is already indexed
"""
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, File, UploadFile

from  app.core.config import get_settings
from  app.core.dependencies import RAGPipelineDep
from  app.generation.pattern_extractor import extract_pattern
from  app.schemas.responses import ExtractPatternResponse, IndexStatusResponse
from  app.services.upload_service import UploadService

router = APIRouter(tags=["Utilities"])
logger = logging.getLogger(__name__)


@router.post(
    "/extract-pattern/",
    response_model=ExtractPatternResponse,
    summary="Extract paper structure from a reference PDF",
)
async def extract_pattern_endpoint(
    pattern_file: UploadFile = File(..., description="Reference question paper PDF"),
):
    """
    Parse a reference question paper PDF and extract its structure:
    total marks, instructions, and section-wise question breakdown.

    Useful for clients to populate the manual_pattern_json field or to
    preview the detected structure before generating a new paper.
    """
    settings = get_settings()
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async with UploadService(settings) as svc:
        pdf_path = await svc.save_one(pattern_file)
        pattern = await extract_pattern(
            pdf_path=pdf_path,
            client=client,
            settings=settings,
        )

    return ExtractPatternResponse(
        total_marks=pattern.total_marks,
        instructions=pattern.instructions,
        question_structure=pattern.question_structure,
    )


@router.post(
    "/index-status/",
    response_model=IndexStatusResponse,
    summary="Check if a file set is already indexed",
)
async def index_status(
    rag: RAGPipelineDep,
    syllabus_files: List[UploadFile] = File(...),
):
    """
    Check whether a given set of sylslabus files is already indexed.

    Returns the composite hash and indexed status. The frontend can use this
    to show a loading indicator only when indexing is actually needed.

    Note: Files are saved temporarily for hashing, then deleted. No indexing
    occurs in this endpoint.
    """
    settings = get_settings()

    async with UploadService(settings) as svc:
        paths = await svc.save(syllabus_files)
        already_indexed = rag.index_exists(paths)
        key = rag.composite_hash(paths)

    return IndexStatusResponse(
        indexed=already_indexed,
        index_key=key,
        file_count=len(syllabus_files),
    )