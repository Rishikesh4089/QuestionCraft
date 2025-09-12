import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import json
from agents.solver import PaperSpecification, create_and_run_agent, ManualPattern
from settings import settings

router = APIRouter()

def save_uploaded_file(file: UploadFile) -> str:
    """Saves a single uploaded file to the UPLOAD_DIR and returns its path."""
    path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path

@router.post("/generate-paper/", tags=["Question Paper Generation"])
async def generate_paper_endpoint(
    subject: str = Form(..., description="The subject of the question paper, e.g., 'Cloud Computing'."),
    syllabus_file: UploadFile = File(..., description="The syllabus PDF document."),
    pattern_file: Optional[UploadFile] = File(None, description="An optional PDF document for the paper pattern.")
):
    """
    Generates a question paper from a syllabus file and a pattern.
    
    You must provide the paper pattern in the following way:
    1.  Upload a **pattern_file**.
    """
    if not pattern_file:
        raise HTTPException(status_code=400, detail="You must provide either a 'pattern_file' or a 'manual_pattern'.")


    syllabus_path = save_uploaded_file(syllabus_file)
    pattern_path = None
    if pattern_file:
        pattern_path = save_uploaded_file(pattern_file)
    
    try:
        spec = PaperSpecification(
            subject=subject,
            syllabus_file_path=syllabus_path,
            pattern_file_path=pattern_path,
        )

        result = await create_and_run_agent(spec)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during agent processing: {str(e)}")

    finally:
        # Cleanup uploaded files
        if os.path.exists(syllabus_path):
            os.remove(syllabus_path)
        if pattern_path and os.path.exists(pattern_path):
            os.remove(pattern_path)