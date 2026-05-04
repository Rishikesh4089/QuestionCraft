# api/v1.py
"""
FastAPI routes for question paper generation.

Endpoints:
  POST /generate-paper/          — Full paper generation (main)
  POST /regenerate-question/     — Regenerate a single question
  POST /regenerate-section/      — Regenerate an entire section
  POST /extract-pattern/         — Extract pattern from a PDF
  GET  /index-status/            — Check if a file set is indexed
"""

import os
import json
import shutil
import logging
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents.solver import (
    PaperSpecification,
    ManualPattern,
    create_and_run_agent,
)
from agents.rag_pipeline import RAGPipeline
from agents.tools import (
    generate_retrieval_queries,
    generate_single_question,
    validate_paper_output,
)
from settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────
# Helper: save uploaded file
# ─────────────────────────────────────────────

def save_uploaded_file(file: UploadFile, upload_dir: str) -> str:
    """Save an uploaded file to disk. Returns the absolute path."""
    os.makedirs(upload_dir, exist_ok=True)
    # Sanitize filename
    safe_name = Path(file.filename).name.replace(" ", "_")
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path


def cleanup_files(paths: List[str]):
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


# ─────────────────────────────────────────────
# Helper: get shared RAG pipeline
# (In production, inject as FastAPI dependency)
# ─────────────────────────────────────────────

def get_pipeline() -> RAGPipeline:
    return RAGPipeline(
        base_index_dir=settings.RAG_INDEX_DIR,
        openai_api_key=settings.OPENAI_API_KEY,
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        cohere_api_key=getattr(settings, "COHERE_API_KEY", None),
        enrich_chunks=False,  # enrichment handled at index-build time
    )


# ─────────────────────────────────────────────
# Endpoint 1: Generate Paper
# ─────────────────────────────────────────────

@router.post("/generate-paper/", tags=["Paper Generation"])
async def generate_paper_endpoint(
    subject: str = Form(...),
    syllabus_files: List[UploadFile] = File(...),
    difficulty_level: Optional[str] = Form(None),
    manual_pattern_json: Optional[str] = Form(None),
    organization: Optional[str] = Form(None),
    program: Optional[str] = Form(None),
    course: Optional[str] = Form(None),
    exam_name: Optional[str] = Form(None),
    exam_date: Optional[str] = Form(None),
    pattern_file: Optional[UploadFile] = File(None),
):
    """
    Generates a structured question paper from syllabus files.

    Accepts:
    - subject: course name
    - syllabus_files: 1+ PDF/PPT/CSV syllabus files
    - manual_pattern_json: JSON string of paper structure (optional)
    - pattern_file: A reference question paper PDF to extract pattern from (optional)
    - difficulty_level: Easy | Medium | Hard | Mixed
    - Paper metadata: organization, program, course, exam_name, exam_date
    """
    syllabus_paths: List[str] = []
    pattern_path: Optional[str] = None

    try:
        # Save uploads
        syllabus_paths = [save_uploaded_file(f, settings.UPLOAD_DIR) for f in syllabus_files]
        logger.info(f"📂 Saved {len(syllabus_paths)} syllabus files")

        if pattern_file:
            pattern_path = save_uploaded_file(pattern_file, settings.UPLOAD_DIR)
            logger.info(f"📄 Saved pattern file: {pattern_path}")

        # Parse manual pattern
        manual_pattern: Optional[ManualPattern] = None
        if manual_pattern_json:
            try:
                pattern_data = json.loads(manual_pattern_json)
                manual_pattern = ManualPattern(**pattern_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid manual_pattern_json: {e}")

        # Build spec
        spec = PaperSpecification(
            subject=subject,
            syllabus_files=syllabus_paths,
            manual_pattern=manual_pattern,
            pattern_file_path=pattern_path,
            difficulty_level=difficulty_level or "Mixed",
            organization=organization,
            program=program,
            course=course,
            exam_name=exam_name,
            exam_date=exam_date,
        )

        logger.info(f"🧠 Running paper generation for: {subject} | Difficulty: {difficulty_level or 'Mixed'}")
        result = await create_and_run_agent(spec)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result.get("detail", result["error"]))

        logger.info("✅ Paper generated successfully")
        return JSONResponse(content=result, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in generate_paper_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    finally:
        cleanup_files(syllabus_paths)
        if pattern_path:
            cleanup_files([pattern_path])


# ─────────────────────────────────────────────
# Endpoint 2: Regenerate Single Question
# ─────────────────────────────────────────────

class RegenerateQuestionBody(BaseModel):
    subject: str
    section: str
    question_type: str
    topic: str
    subtopic: Optional[str] = None
    bloom_level: Optional[str] = "Apply"
    difficulty_level: Optional[str] = "Medium"
    marks: Optional[int] = 5
    previous_questions: Optional[List[str]] = []
    syllabus_file_hashes: Optional[List[str]] = []  # for index lookup without reuploading


@router.post("/regenerate-question/", tags=["Regeneration"])
async def regenerate_question_endpoint(payload: RegenerateQuestionBody = Body(...)):
    """
    Regenerates a single question given topic, type, and difficulty.
    Uses the existing indexed syllabus — does NOT require re-uploading files.
    The client should pass the same syllabus file paths used during paper generation.
    """
    try:
        pipeline = get_pipeline()

        # Retrieve context using the active (already-built) index
        # NOTE: index must have been built already — regeneration doesn't rebuild it
        if pipeline._active_hash is None and not pipeline._cache:
            raise HTTPException(
                status_code=400,
                detail="No syllabus indexed. Generate a paper first, or pass syllabus files."
            )

        subtopic = payload.subtopic or payload.topic
        queries = await generate_retrieval_queries(
            topic=payload.topic,
            subtopic=subtopic,
            question_type=payload.question_type,
            bloom_level=payload.bloom_level or "Apply",
        )

        chunks = await pipeline.multi_query_retrieve(
            queries=queries,
            k=8,
            rerank_top_n=4,
            max_context_tokens=1800,
        )
        context = pipeline.build_context_string(chunks) if chunks else f"Topic: {payload.topic}"

        question = await generate_single_question(
            context=context,
            subject=payload.subject,
            topic=payload.topic,
            subtopic=subtopic,
            question_type=payload.question_type,
            bloom_level=payload.bloom_level or "Apply",
            marks=payload.marks or 5,
            difficulty=payload.difficulty_level or "Medium",
            previous_questions=payload.previous_questions or [],
        )

        logger.info(f"✅ Question regenerated: {question.topic}")
        return {"success": True, "new_question": question.model_dump()}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in regenerate_question_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# ─────────────────────────────────────────────
# Endpoint 3: Regenerate Entire Section
# ─────────────────────────────────────────────

class RegenerateSectionBody(BaseModel):
    subject: str
    section: str
    question_type: str
    difficulty_level: Optional[str] = "Medium"
    marks_each: Optional[int] = 5
    questions: List[Dict[str, Any]]  # existing questions (to extract topics from)


@router.post("/regenerate-section/", tags=["Regeneration"])
async def regenerate_section_endpoint(payload: RegenerateSectionBody = Body(...)):
    """
    Regenerates all questions in a section.
    Extracts topics from the existing questions, then regenerates each
    with proper context retrieval and dedup logic.
    """
    try:
        pipeline = get_pipeline()

        if pipeline._active_hash is None and not pipeline._cache:
            raise HTTPException(
                status_code=400,
                detail="No syllabus indexed. Generate a paper first."
            )

        # Extract topic slots from existing questions
        from agents.solver import QuestionSlot
        slots = []
        for i, q in enumerate(payload.questions):
            topic = q.get("topic", "General")
            subtopic = q.get("subtopic", topic)
            bloom_level = q.get("blooms_taxonomy_level", "Apply")
            slots.append(QuestionSlot(
                section=payload.section,
                slot_index=i,
                topic=topic,
                subtopic=subtopic,
                bloom_level=bloom_level,
                marks=payload.marks_each or q.get("marks", 5),
                question_type=payload.question_type,
                difficulty=payload.difficulty_level or "Medium",
            ))

        # Generate section using the same logic as full paper generation
        from agents.solver import _generate_section
        model = getattr(settings, "GENERATION_MODEL_NAME", "gpt-4o-mini")
        new_section = await _generate_section(
            section_name=payload.section,
            slots=slots,
            retriever=pipeline,
            subject=payload.subject,
            question_model=model,
        )

        logger.info(f"✅ Section {payload.section} regenerated: {len(new_section.questions)} questions")
        return JSONResponse(content={"section": new_section.model_dump()}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in regenerate_section_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# ─────────────────────────────────────────────
# Endpoint 4: Extract Pattern from PDF
# ─────────────────────────────────────────────

@router.post("/extract-pattern/", tags=["Utilities"])
async def extract_pattern_endpoint(
    pattern_file: UploadFile = File(...),
):
    """
    Extracts the question paper structure (pattern) from an uploaded PDF.
    Returns total marks, instructions, and section breakdown.
    """
    saved_path = None
    try:
        saved_path = save_uploaded_file(pattern_file, settings.UPLOAD_DIR)
        from agents.tools import extract_paper_pattern_tool
        pattern_data = await extract_paper_pattern_tool.run_async(file_path=saved_path)
        return JSONResponse(content=pattern_data, status_code=200)
    except Exception as e:
        logger.exception(f"Error in extract_pattern_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern extraction failed: {str(e)}")
    finally:
        if saved_path:
            cleanup_files([saved_path])


# ─────────────────────────────────────────────
# Endpoint 5: Validate Paper
# ─────────────────────────────────────────────

class ValidatePaperBody(BaseModel):
    paper: Dict[str, Any]
    question_structure: List[Dict[str, Any]]
    expected_total_marks: int


@router.post("/validate-paper/", tags=["Utilities"])
async def validate_paper_endpoint(payload: ValidatePaperBody = Body(...)):
    """
    Validates a generated paper against expected structure.
    Returns list of errors (empty list = valid).
    """
    try:
        errors = validate_paper_output(
            sections=payload.paper.get("sections", []),
            question_structure=payload.question_structure,
            expected_total_marks=payload.expected_total_marks,
        )
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")


# ─────────────────────────────────────────────
# Endpoint 6: Index Status
# ─────────────────────────────────────────────

@router.post("/index-status/", tags=["Utilities"])
async def index_status_endpoint(
    syllabus_files: List[UploadFile] = File(...),
):
    """
    Check if a given set of syllabus files is already indexed.
    Returns the composite hash and indexed status.
    Useful for the frontend to show a loading indicator only if indexing is needed.
    """
    saved_paths = []
    try:
        saved_paths = [save_uploaded_file(f, settings.UPLOAD_DIR) for f in syllabus_files]
        pipeline = get_pipeline()
        already_indexed = pipeline.index_exists(saved_paths)
        from agents.rag_pipeline import composite_hash
        c_hash = composite_hash(saved_paths)
        return {
            "indexed": already_indexed,
            "composite_hash": c_hash,
            "file_count": len(saved_paths),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_files(saved_paths)