# app/api/v1/paper.py
"""
Paper generation endpoints.

POST /generate-paper/  — Full paper generation
POST /validate-paper/  — Structural validation of an existing paper
"""
from __future__ import annotations

import json
import logging
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from  app.core.config import Settings, get_settings
from  app.core.dependencies import RAGPipelineDep
from  app.core.exceptions import QuestionCraftError
from  app.schemas.pattern import ManualPattern
from  app.schemas.requests import ValidatePaperRequest
from  app.schemas.responses import GeneratePaperResponse, ValidatePaperResponse
from  app.services.paper_service import PaperService
from  app.services.upload_service import UploadService
from  app.generation.validator import validate_paper

router = APIRouter(tags=["Paper Generation"])
logger = logging.getLogger(__name__)


@router.post(
    "/generate-paper/",
    response_model=GeneratePaperResponse,
    summary="Generate a question paper from syllabus files",
)
async def generate_paper(
    rag: RAGPipelineDep,
    subject: str = Form(..., description="Course/subject name"),
    syllabus_files: List[UploadFile] = File(..., description="Syllabus documents (PDF/PPTX/CSV/TXT)"),
    difficulty_level: Optional[str] = Form(None, description="Easy | Medium | Hard | Mixed"),
    manual_pattern_json: Optional[str] = Form(None, description="JSON string of ManualPattern"),
    organization: Optional[str] = Form(None),
    program: Optional[str] = Form(None),
    course: Optional[str] = Form(None),
    exam_name: Optional[str] = Form(None),
    exam_date: Optional[str] = Form(None),
    pattern_file: Optional[UploadFile] = File(None, description="Reference paper PDF for pattern extraction"),
):
    """
    Generate a complete question paper.

    Accepts one or more syllabus files and returns a structured paper JSON.
    The response includes `index_key` — pass it to /regenerate-question/ or
    /regenerate-section/ to avoid re-uploading the syllabus.

    If neither `manual_pattern_json` nor `pattern_file` is provided, a sensible
    default structure (3 sections, 80 marks) is used.
    """
    settings = get_settings()

    manual_pattern: Optional[ManualPattern] = None
    if manual_pattern_json:
        try:
            manual_pattern = ManualPattern(**json.loads(manual_pattern_json))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid manual_pattern_json: {exc}")

    async with UploadService(settings) as upload_svc:
        syllabus_paths = await upload_svc.save(syllabus_files)
        pattern_path = await upload_svc.save_one(pattern_file) if pattern_file else None

        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        service = PaperService(rag=rag, client=client, settings=settings)

        result = await service.generate(
            subject=subject,
            syllabus_paths=syllabus_paths,
            difficulty=difficulty_level or "Mixed",
            manual_pattern=manual_pattern,
            pattern_pdf_path=pattern_path,
            organization=organization or "",
            program=program or "",
            course=course or "",
            exam_name=exam_name or "",
            exam_date=exam_date or "",
        )

    return GeneratePaperResponse(**result)


@router.post(
    "/validate-paper/",
    response_model=ValidatePaperResponse,
    summary="Validate a paper against its expected structure",
)
async def validate_paper_endpoint(payload: ValidatePaperRequest):
    """
    Validate a generated (or manually constructed) paper.

    Returns a list of structural errors. An empty list means the paper is valid.
    Useful for client-side validation before rendering or exporting.
    """
    errors = validate_paper(
        sections=payload.paper.get("sections", []),
        question_structure=payload.question_structure,
        expected_total_marks=payload.expected_total_marks,
    )
    return ValidatePaperResponse(valid=not errors, errors=errors)