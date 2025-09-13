from agno.tools import tool
from pydantic import BaseModel, Field
from typing import List
from agno.models.openai import OpenAIChat
from settings import settings
import json
import pypdf

#--- COMMENTED OUT: Imports for Gemini ---
# import google.generativeai as genai

#--- COMMENTED OUT: Configure the Gemini client ---
# genai.configure(api_key=settings.GEMINI_API_KEY)
# tool_llm = genai.GenerativeModel('gemini-1.5-pro-latest')


# --- Pydantic Models for Structured Tool I/O (No changes) ---
class Question(BaseModel):
    question_text: str = Field(..., description="The full text of the generated question.")
    marks: int = Field(..., description="The marks allocated for this question.")
    blooms_taxonomy_level: str = Field(..., description="The assessed Bloom's Taxonomy level (e.g., 'Applying', 'Analyzing').")
    topic: str = Field(..., description="The specific topic from the syllabus this question addresses.")

class PaperPattern(BaseModel):
    total_marks: int = Field(..., description="Total marks for the paper.")
    instructions: List[str] = Field(..., description="List of instructions for the students.")
    question_structure: List[dict] = Field(..., description="A list defining each main question, its marks, and number of sub-questions.")


# --- LLM Client for Tools (Switched to OpenAI) ---
tool_llm = OpenAIChat(
    id=settings.GENERATION_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY,
    temperature=0.7
)

# --- Agent Tools (Now fully powered by OpenAI) ---

@tool
async def extract_paper_pattern_tool(file_path: str) -> PaperPattern:
    """
    Reads a PDF document, extracts its text, and uses the OpenAI LLM to analyze and
    determine the question paper's structure, instructions, and total marks.
    """
    print(f"🤖--- Running LIVE Pattern Extraction on: {file_path} with OpenAI ---")
    try:
        reader = pypdf.PdfReader(file_path)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        
        if not text_content.strip():
            raise ValueError("Could not extract any text from the PDF.")

        prompt = f"""
        You are an expert at parsing academic documents. Analyze the following text extracted from a question paper and identify its structure.

        **Extracted Text:**
        ---
        {text_content[:4000]}
        ---

        Based on the text, respond with a single JSON object containing the exact keys: "total_marks", "instructions", and "question_structure".
        - "total_marks" should be an integer.
        - "instructions" should be a list of strings.
        - "question_structure" should be a list of objects describing the questions (e.g., marks, number of sub-questions, type like compulsory/optional).
        """
        
        #- UPDATED: Call the OpenAIChat tool_llm and parse the response
        # This assumes the .chat() method returns a raw text response.
        response_text = await tool_llm.chat(prompt)

        # Clean up potential markdown formatting from the OpenAI response
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:-3]
            
        data = json.loads(response_text)
        
        return PaperPattern(**data)

    except Exception as e:
        print(f"ERROR in extract_paper_pattern_tool: {e}. Returning a fallback pattern.")
        return PaperPattern(
            total_marks=100,
            instructions=["Error: Could not parse pattern file. Using fallback."],
            question_structure=[{"type": " fallback", "count": 5, "marks": 20}]
        )

@tool
async def generate_question_tool(context: str, question_type: str, marks: int, topic: str, subject: str) -> Question:
    """
    Generates a single, university-level question by calling the OpenAI API.
    """
    print(f"🤖 Generating a LIVE '{question_type}' question for topic: {topic} via OpenAI API")
    
    prompt = f"""
    You are a question generation expert. Based on the provided context from the syllabus of the subject '{subject}', create one high-quality, descriptive, university-level question.

    **Rules:**
    1.  **Question Type**: Must be a '{question_type}' answer type.
    2.  **Strictly Prohibited**: Do NOT generate Multiple-Choice Questions (MCQs), fill-in-the-blanks, or matching questions.
    3.  **Topic Focus**: The question must be about: '{topic}'.
    4.  **Marks**: The question will be for {marks} marks. The complexity must match the marks.
    5.  **Grounded in Context**: The question must be answerable using ONLY the provided context.
    6.  **Bloom's Taxonomy**: Assess your own question and assign it a Bloom's Taxonomy level (Remembering, Understanding, Applying, Analyzing, Evaluating, Creating).

    **Context from Syllabus:**
    ---
    {context}
    ---

    Respond with a single JSON object with the following exact keys: "question_text", "blooms_taxonomy_level".
    """
    
    try:
        #- UPDATED: Use the shared OpenAIChat tool_llm and parse the response
        response_text = await tool_llm.chat(prompt)

        # Clean up potential markdown formatting
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:-3]

        data = json.loads(response_text)
        
        return Question(
            question_text=data["question_text"],
            marks=marks,
            blooms_taxonomy_level=data["blooms_taxonomy_level"],
            topic=topic
        )
    except Exception as e:
        print(f"Error parsing OpenAI response for question generation: {e}. Using fallback.")
        return Question(
            question_text=f"Explain the key aspects of {topic}. [Fallback Question]",
            marks=marks,
            blooms_taxonomy_level="Understanding",
            topic=topic
        )