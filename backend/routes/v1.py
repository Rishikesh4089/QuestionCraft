import os
import shutil
import json
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI

# Core imports
from agents.solver import PaperSpecification, create_and_run_agent, ManualPattern
from agents.rag_pipeline import RAGPipeline
from agents.tools import generate_single_question_tool, regenerate_section_tool
from settings import settings

router = APIRouter()


# ============================================================
# 🧰 Helper: Save Uploaded File
# ============================================================

def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return its absolute path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path


# ============================================================
# 🔁 1️⃣ Regenerate a Single Question (Clean + Reliable)
# ============================================================

class RegenerateQuestionBody(BaseModel):
    subject: str
    section: str
    question_type: str
    topic: str
    difficulty_level: str
    previous_questions: List[str]


@router.post("/regenerate-question/", tags=["Question Regeneration"])
async def regenerate_question_endpoint(payload: RegenerateQuestionBody = Body(...)):
    """
    Generates a single new question based on topic, section, and difficulty.
    Uses new tool: generate_single_question_tool
    """
    try:
        print(f"♻️ Regenerating question for {payload.subject} | Section: {payload.section}")

        # Initialize RAG pipeline
        openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=getattr(settings, "OPENAI_BASE_URL", None),
        )

        pipeline = RAGPipeline(
            index_dir=settings.RAG_INDEX_DIR,
            embedding_client=openai_client,
            embedding_model=settings.EMBEDDING_MODEL_NAME,
        )

        # Retrieve syllabus context
        context_chunks = pipeline.retrieve_context(
            f"{payload.topic} {payload.question_type}", k=5
        )
        context_text = "\n\n".join([c["text"] for c in context_chunks]) or "No relevant context found."

        # ✅ Use .run_async() explicitly to avoid decorator call error
        if hasattr(generate_single_question_tool, "run_async"):
            new_question = await generate_single_question_tool.run_async(
                context=context_text,
                subject=payload.subject,
                topic=payload.topic,
                question_type=payload.question_type,
                difficulty=payload.difficulty_level,
                marks=5,
                previous_questions=payload.previous_questions,
            )
        else:
            raise RuntimeError("generate_single_question_tool has no .run_async()")

        print("✅ New question generated successfully.")
        return {"success": True, "new_question": new_question}

    except Exception as e:
        print(f"❌ Error regenerating question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# ============================================================
# 🔁 2️⃣ Regenerate an Entire Section (Parallelized)
# ============================================================

@router.post("/regenerate-section/", tags=["Question Regeneration"])
async def regenerate_section_endpoint(section: Dict[str, Any] = Body(...)):
    """
    Regenerates an entire section of questions using regenerate_section_tool.
    Uses parallel async regeneration for better performance.
    """
    try:
        section_name = section.get("section")
        question_type = section.get("question_type", "General")
        difficulty_level = "Medium"
        topics = [q.get("topic", "General Topic") for q in section.get("questions", [])]

        print(f"♻️ Regenerating entire section: {section_name} ({len(topics)} questions)")

        # Dummy context (replace with real RAG retrieval if needed)
        context_text = "Core syllabus content for section context."

        # ✅ Explicit run_async usage
        if hasattr(regenerate_section_tool, "run_async"):
            new_section = await regenerate_section_tool.run_async(
                context=context_text,
                subject="Unknown",
                section_name=section_name,
                question_type=question_type,
                topics=topics,
                marks_each=5,
                difficulty=difficulty_level,
            )
        else:
            raise RuntimeError("regenerate_section_tool has no .run_async()")

        print(f"✅ Section {section_name} regenerated successfully.")
        return JSONResponse(content={"section": new_section}, status_code=200)

    except Exception as e:
        print(f"❌ Error regenerating section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# ============================================================
# 🚀 3️⃣ Generate Question Paper (Main Endpoint)
# ============================================================

@router.post("/generate-paper/", tags=["Question Paper Generation"])
async def generate_paper_endpoint(
    subject: str = Form(...),
    syllabus_files: List[UploadFile] = File(...),
    difficulty_level: Optional[str] = Form(None),
    manual_pattern_json: Optional[str] = Form(None),

    # ✅ Added metadata fields
    organization: Optional[str] = Form(None),
    program: Optional[str] = Form(None),
    course: Optional[str] = Form(None),
    exam_name: Optional[str] = Form(None),
    exam_date: Optional[str] = Form(None),
):
    """
    Generates a structured question paper using syllabus files and JSON pattern parameters.
    """
    syllabus_paths = []
    try:
        syllabus_paths = [save_uploaded_file(f) for f in syllabus_files]
        print(f"📘 Uploaded syllabus saved to: {syllabus_paths}")

        manual_pattern = None
        total_marks = 0
        if manual_pattern_json:
            manual_pattern_data = json.loads(manual_pattern_json)
            total_marks = manual_pattern_data.get("total_marks", 0)
            manual_pattern = ManualPattern(**manual_pattern_data)

        # ✅ Build the paper specification
        spec = PaperSpecification(
            subject=subject,
            syllabus_files=syllabus_paths,
            manual_pattern=manual_pattern,
            pattern_file_path=None,
            difficulty_level=difficulty_level,
            organization=organization,
            program=program,
            course=course,
            exam_name=exam_name,
            exam_date=exam_date,
        )

        print(f"🧠 Running RAG agent for subject: {subject} | Difficulty: {difficulty_level or 'Mixed'}")
        result = await create_and_run_agent(spec)

        # ✅ Inject metadata fields into final response
        result.update({
            "organization": organization or "N/A",
            "program": program or "N/A",
            "course": course or "N/A",
            "exam_name": exam_name or "N/A",
            "exam_date": exam_date or "N/A",
            "subject": subject,
            "total_marks": total_marks,
        })

        print("✅ Question paper generated successfully.")
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        print(f"❌ Error generating paper: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    finally:
        for path in syllabus_paths:
            if os.path.exists(path):
                os.remove(path)
