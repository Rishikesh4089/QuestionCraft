import json
import asyncio
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
from openai import OpenAI
from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat

from agents.rag_pipeline import RAGPipeline
from agents.tools import generate_question_simple, extract_paper_pattern_tool
from agents.utils.json_utils import extract_json_from_text, safe_json_loads
from settings import settings


# ================================================
# 🧩 Pydantic Models
# ================================================
class Question(BaseModel):
    text: str
    marks: int
    blooms_taxonomy_level: str
    topic: str

class Section(BaseModel):
    section: str
    question_type: str
    questions: List[Question]

class PaperOutput(BaseModel):
    subject: str
    total_marks: int
    instructions: Optional[List[str]]
    sections: List[Section]

class ManualPattern(BaseModel):
    total_marks: int
    instructions: Optional[List[str]] = None
    question_structure: Optional[List[dict]] = None

class PaperSpecification(BaseModel):
    subject: str
    syllabus_files: List[str]               # local paths
    pattern_file_path: Optional[str] = None
    manual_pattern: Optional[ManualPattern] = None
    difficulty_level: Optional[str] = None


# ================================================
# ⚙️ LLM + Embedding Clients
# ================================================
openai_client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=getattr(settings, "OPENAI_BASE_URL", None)
)
llm_chat = OpenAIChat(
    id=settings.GENERATION_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.3
)


# ================================================
# 🎓 Strong Agent Prompt
# ================================================
AGENT_INSTRUCTIONS = """
You are a highly experienced university examiner and paper setter.

Your goal:
Construct a complete, well-structured question paper using the provided syllabus context and the given JSON pattern (question_structure).

Inputs you receive include:
- Organization, Program, Course, Subject, Exam Date
- Difficulty level
- A question pattern JSON, containing any number of sections with fields:
    [
      {
        "section": "A",
        "question_type": "Short Answer",
        "marks_each": 4,
        "question_count": 5
      },
      {
        "section": "B",
        "question_type": "Long Answer",
        "marks_each": 10,
        "question_count": 3
      },
      ...
    ]

Guidelines:
1. Generate the correct number of questions per section according to question_count.
2. Each question must align with the syllabus context and the specified question_type.
3. Maintain total marks equal to total_marks.
4. Use Bloom’s Taxonomy level (e.g., Remembering, Understanding, Applying, Evaluating, Creating).
5. Return strictly valid JSON — no text outside JSON.

Your output JSON schema must look like this:

{
  "organization": "<organization>",
  "program": "<program>",
  "course": "<course>",
  "exam_date": "<exam_date>",
  "subject": "<subject>",
  "total_marks": <int>,
  "instructions": ["..."],
  "sections": [
    {
      "section": "<section_name>",
      "question_type": "<question_type>",
      "questions": [
        {
          "text": "<question_text>",
          "marks": <int>,
          "blooms_taxonomy_level": "<level>",
          "topic": "<topic_from_syllabus>"
        }
      ]
    }
  ]
}

Ensure:
- The number of questions and marks in each section strictly match the question_structure.
- Total marks = total_marks.
- Include all sections listed in the input pattern.
- Do not include explanations — only valid JSON.
"""

# ================================================
# 🚀 Main Agent Function
# ================================================
async def create_and_run_agent(spec: PaperSpecification) -> Dict[str, Any]:
    try:
        # --- 1️⃣ Build and index RAG context ---
        pipeline = RAGPipeline(
            index_dir=settings.RAG_INDEX_DIR,
            embedding_client=openai_client,
            embedding_model=settings.EMBEDDING_MODEL_NAME
        )
        pipeline.add_files(spec.syllabus_files, doc_id_prefix=spec.subject.replace(" ", "_"), reindex=True)

        # --- 2️⃣ Retrieve context safely ---
        context_chunks = pipeline.retrieve_context(f"Comprehensive overview of {spec.subject}", k=8)
        context_text = "\n\n".join([c["text"] for c in context_chunks]) or "No syllabus context found."

        # --- 3️⃣ Prepare pattern info ---
        pattern_json = spec.manual_pattern.dict() if spec.manual_pattern else {}
        pattern_str = json.dumps(pattern_json, indent=2)

        # --- 4️⃣ Construct agent prompt ---
       # --- 4️⃣ Construct agent prompt ---
        goal_prompt = f"""
            {AGENT_INSTRUCTIONS}

            📘 Syllabus Context (use only for factual grounding):
            {context_text}

            🧩 Paper Metadata:
            Organization: {getattr(spec, 'organization', 'N/A')}
            Program: {getattr(spec, 'program', 'N/A')}
            Course: {getattr(spec, 'course', 'N/A')}
            Exam Date: {getattr(spec, 'exam_date', 'N/A')}
            Subject: {spec.subject}
            Difficulty Level: {spec.difficulty_level or 'Mixed'}

            📄 Question Pattern JSON (strictly follow this structure):
            {pattern_str}

            Generate the final question paper JSON **exactly following** the schema and constraints:
            - Include all metadata above.
            - Include all sections listed in question_structure.
            - Ensure marks per question and total marks match.
            - Use syllabus topics for realism.
            - Output only valid JSON — no text before or after.
            """


        # --- 5️⃣ Initialize Agent ---
        agent = Agent(
            model=llm_chat,
            instructions=goal_prompt,
            tools=[extract_paper_pattern_tool, generate_question_simple],
            debug_mode=True
        )

        # --- 6️⃣ Run generation ---
        response: RunOutput = await agent.arun(goal_prompt)
        raw_output = response.content.strip()

        # --- 7️⃣ Extract & clean JSON ---
        json_str = extract_json_from_text(raw_output)
        data = safe_json_loads(json_str)

        # --- 8️⃣ Validate structure ---
        try:
            paper = PaperOutput.model_validate(data)
            print("✅ Question paper generated successfully.")
            return paper.model_dump()
        except ValidationError as ve:
            # Validation failed but we have valid JSON → return partial
            print("⚠️ JSON parsed but validation failed:", ve)
            return {"error": "Invalid paper schema", "raw": data, "validation_error": ve.errors()}

    except Exception as e:
        print("❌ Error generating paper:", str(e))
        return {"error": "Agent run failed", "detail": str(e)}
