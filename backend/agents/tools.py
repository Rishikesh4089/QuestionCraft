import json
import pypdf
from pydantic import BaseModel, Field
from typing import List
from agno.tools import tool


from agno.models.openai import OpenAIChat
from settings import settings

# ============================================================
# 🧩 Optional OCR imports (for scanned PDFs)
# ============================================================

try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    convert_from_path = None
    pytesseract = None


# ============================================================
# 🧩 Structured Data Models
# ============================================================

class Question(BaseModel):
    question_text: str = Field(..., description="Full text of the generated question.")
    marks: int = Field(..., description="Marks allocated for this question.")
    blooms_taxonomy_level: str = Field(..., description="Bloom's taxonomy level.")
    topic: str = Field(..., description="Specific topic from the syllabus.")


class PaperPattern(BaseModel):
    total_marks: int = Field(..., description="Total marks for the paper.")
    instructions: List[str] = Field(..., description="Instructions for students.")
    question_structure: List[dict] = Field(
        ..., description="List describing sections, marks, and sub-question counts."
    )


# ============================================================
# ⚙️ Shared LLM Client (OpenAI)
# ============================================================

tool_llm = OpenAIChat(
    id=settings.GENERATION_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3,
)


# ============================================================
# 🧠 Tool #1: Extract Paper Pattern
# ============================================================

async def extract_paper_pattern_tool(file_path: str) -> PaperPattern:
    """
    Reads a question paper (PDF) and extracts its structure — total marks,
    instructions, and question sections — using OpenAI.
    Includes OCR fallback for scanned PDFs.
    """
    print(f"🤖 Extracting paper pattern from: {file_path}")
    try:
        text_content = ""

        # --- Step 1: Try normal PDF text extraction ---
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    text_content += txt + "\n"
        except Exception as e:
            print(f"⚠️ PyPDF failed to read: {e}")

        # --- Step 2: OCR fallback if text missing ---
        if not text_content.strip() and convert_from_path and pytesseract:
            print("🔍 Running OCR fallback...")
            try:
                images = convert_from_path(file_path)
                for img in images:
                    text_content += pytesseract.image_to_string(img)
            except Exception as e:
                print(f"⚠️ OCR fallback failed: {e}")

        if not text_content.strip():
            raise ValueError("No readable text found in PDF (possibly a scanned image).")

        # --- Step 3: Ask LLM to analyze pattern ---
        prompt = f"""
        You are an expert at understanding university question paper formats.
        Read the following question paper text and extract:
        1. Total marks
        2. Instructions
        3. Section-wise structure (section name, number of questions, marks per question)

        Respond ONLY in **valid JSON**, following this schema:
        {{
          "total_marks": 100,
          "instructions": ["Instruction 1", "Instruction 2"],
          "question_structure": [
            {{"section": "A", "question_count": 5, "marks_each": 4}},
            {{"section": "B", "question_count": 2, "marks_each": 10}},
            {{"section": "C", "question_count": 2, "marks_each": 10}},
            {{"section": "D", "question_count": 2, "marks_each": 10}},
            {{"section": "E", "question_count": 2, "marks_each": 10}}
          ]
        }}

        Do NOT include any commentary or explanation, only JSON.

        ---
        {text_content[:3500]}
        ---
        """

        response_text = await tool_llm.generate(prompt)
        response_text = response_text.strip()

        # --- Step 4: Clean possible code block wrappers ---
        if response_text.startswith("```json"):
            response_text = response_text.removeprefix("```json").removesuffix("```").strip()
        elif response_text.startswith("```"):
            response_text = response_text.removeprefix("```").removesuffix("```").strip()

        # --- Step 5: Try parsing JSON ---
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                recovered = response_text[start:end]
                data = json.loads(recovered)
            else:
                raise

        # --- Step 6: Return structured pattern ---
        return PaperPattern(**data)

    except Exception as e:
        print(f"❌ ERROR in extract_paper_pattern_tool: {e}")
        return PaperPattern(
            total_marks=100,
            instructions=[
                "Answer all questions from Section A and any two from each of the remaining sections.",
                "Figures to the right indicate full marks.",
                "Assume suitable data wherever required.",
                "All questions carry equal marks unless specified."
            ],
            question_structure=[
                {"section": "A", "question_count": 5, "marks_each": 4},
                {"section": "B", "question_count": 2, "marks_each": 10},
                {"section": "C", "question_count": 2, "marks_each": 10},
                {"section": "D", "question_count": 2, "marks_each": 10},
                {"section": "E", "question_count": 2, "marks_each": 10}
            ],
        )


# ============================================================
# 🧠 Tool #2: Generate Question (for Agent)
# ============================================================

@tool
async def generate_question_simple(
    context: str,
    question_type: str,
    marks: int,
    topic: str,
    subject: str
) -> dict:
    """
    Lightweight wrapper that calls `generate_question_simple`
    and returns a validated dict output for the agent to consume.

    This tool ensures:
    - consistent JSON schema for question generation
    - safe fallback if `generate_question_simple` fails
    - easier chaining inside solver.py’s agent execution
    """
    try:
        # Call the main question generator (already defined)
        q = await generate_question_simple(
            context=context,
            question_type=question_type,
            marks=marks,
            topic=topic,
            subject=subject,
        )

        # Convert to dict if it's a Pydantic BaseModel
        if hasattr(q, "model_dump"):
            return q.model_dump()
        elif hasattr(q, "dict"):
            return q.dict()

        # If it’s already a dict or JSON string, normalize
        if isinstance(q, dict):
            return q
        elif isinstance(q, str):
            try:
                return json.loads(q)
            except json.JSONDecodeError:
                pass

        # Final fallback if no structured data
        return {
            "question_text": f"Explain the topic {topic} in detail.",
            "marks": marks,
            "blooms_taxonomy_level": "Understanding",
            "topic": topic,
        }

    except Exception as e:
        print(f"⚠️ generate_question_simple failed: {e}")
        return {
            "question_text": f"Describe {topic} briefly. [Fallback]",
            "marks": marks,
            "blooms_taxonomy_level": "Remembering",
            "topic": topic,
        }
    
# ============================================================
# 🧠 Tool #3: Generate a Single Question (Standalone, No Recursion)
# ============================================================

@tool
async def generate_single_question_tool(
    context: str,
    subject: str,
    topic: str,
    question_type: str,
    difficulty: str = "Medium",
    marks: int = 5,
    previous_questions: List[str] = None,
) -> dict:
    """
    Generates a single NEW question based on topic, question type, and difficulty.
    Ensures it's not a duplicate of previously asked questions.
    """
    previous_questions = previous_questions or []

    try:
        prompt = f"""
You are a senior university examiner generating ONE new question.

Context (syllabus content):
{context}

Generate ONE new question that:
- Belongs to Subject: {subject}
- Question Type: {question_type}
- Topic: {topic}
- Difficulty: {difficulty}
- Is NOT similar to these questions:
{json.dumps(previous_questions, indent=2)}

Return ONLY valid JSON in this format:
{{
  "text": "<question text>",
  "marks": {marks},
  "blooms_taxonomy_level": "<Bloom's taxonomy level>",
  "topic": "{topic}"
}}
"""

        # Use shared LLM client
        response = await tool_llm.generate(prompt)
        response_text = response.strip()

        # Clean up formatting if wrapped in code blocks
        if response_text.startswith("```json"):
            response_text = response_text.removeprefix("```json").removesuffix("```").strip()
        elif response_text.startswith("```"):
            response_text = response_text.removeprefix("```").removesuffix("```").strip()

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to recover JSON substring if LLM adds extra text
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                recovered = response_text[start:end]
                data = json.loads(recovered)
            else:
                raise

        # Validation / fallback
        if not isinstance(data, dict) or "text" not in data:
            raise ValueError("Invalid JSON format returned by LLM")

        return data

    except Exception as e:
        print(f"⚠️ generate_single_question_tool failed: {e}")
        return {
            "text": f"Explain {topic} briefly. [Fallback]",
            "marks": marks,
            "blooms_taxonomy_level": "Remembering",
            "topic": topic,
        }


# ============================================================
# 🧠 Tool #4: Regenerate Section (Multiple Questions)
# ============================================================

@tool
async def regenerate_section_tool(
    context: str,
    subject: str,
    section_name: str,
    question_type: str,
    topics: List[str],
    marks_each: int = 5,
    difficulty: str = "Medium",
) -> dict:
    """
    Regenerates an entire section with multiple questions in parallel.
    Each question is unique and topic-aligned.
    """
    try:
        print(f"♻️ Regenerating section {section_name} ({len(topics)} questions)")

        async def generate_for_topic(topic: str):
            q_data = await generate_single_question_tool.run_async(
                context=context,
                subject=subject,
                topic=topic,
                question_type=question_type,
                marks=marks_each,
                difficulty=difficulty,
                previous_questions=[],
            )
            return q_data

        import asyncio
        results = await asyncio.gather(*[generate_for_topic(t) for t in topics])

        section_data = {
            "section": section_name,
            "question_type": question_type,
            "questions": results,
        }

        return section_data

    except Exception as e:
        print(f"❌ regenerate_section_tool failed: {str(e)}")
        return {
            "section": section_name,
            "question_type": question_type,
            "questions": [],
            "error": str(e),
        }