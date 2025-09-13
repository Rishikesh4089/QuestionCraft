import json
from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- COMMENTED OUT: NEW IMPORTS for Gemini ---
# import google.generativeai as genai

from .tools import extract_paper_pattern_tool, generate_question_tool
from rag.pipeline import RAGPipeline
from settings import settings

# --- Pydantic Models (No changes here) ---
class ManualPattern(BaseModel):
    total_marks: int
    questions: List[Dict[str, Any]]

class PaperSpecification(BaseModel):
    subject: str
    syllabus_file_path: str
    pattern_file_path: Optional[str] = None
    manual_pattern: Optional[ManualPattern] = None

# --- Agent Instructions (No changes here) ---
AGENT_INSTRUCTIONS = """
You are a meticulous and highly experienced University Professor...
"""

# --- COMMENTED OUT: Gemini Model Wrapper ---
# This class makes the Gemini model compatible with the agno.Agent,
# which expects a model object with an `arun` method.
# class GeminiModelForAgent:
#     def __init__(self, model_name: str, api_key: str):
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel(model_name)
# 
#     async def arun(self, prompt: str) -> RunOutput:
#         """
#         Runs the Gemini model and formats the output for the agno.Agent.
#         """
#         print("🤖 Agent is thinking with Gemini...")
#         response = await self.model.generate_content_async(prompt)
#         # The agno.Agent expects a RunOutput object. We provide the Gemini
#         # response text to its 'content' field.
#         return RunOutput(content=response.text, tool_calls=None)

async def create_and_run_agent(specification: PaperSpecification) -> Dict[str, Any]:
    rag_pipeline = None
    try:
        # --- Step 1: Initialize RAG Pipeline (No changes here) ---
        print("Initializing RAG pipeline with FAISS index...")
        rag_pipeline = RAGPipeline(file_paths=[specification.syllabus_file_path])

        # --- Step 2: Configure the LLM and Agent (Reverted to OpenAI) ---
        print(f"🤖 Configuring agent with OpenAI model...")
        
        # The agent will now use this OpenAI model
        llm = OpenAIChat(
            id='gpt-4.1', # You can use settings.GENERATION_MODEL_NAME here
            api_key=settings.OPENAI_API_KEY
        )

        # --- COMMENTED OUT: Gemini model instantiation ---
        # llm = GeminiModelForAgent(
        #     model_name='gemini-1.5-pro-latest',
        #     api_key=settings.GEMINI_API_KEY
        # )

        agent = Agent(
            model=llm, # The agent now uses the OpenAIChat model
            instructions=AGENT_INSTRUCTIONS,
            tools=[extract_paper_pattern_tool, generate_question_tool],
            debug_mode=True
        )

        # --- Step 3: Create Master Prompt (No changes here) ---
        initial_context = rag_pipeline.retrieve_context(query=f"General overview of the subject: {specification.subject}")
        
        pattern_instruction = ""
        if specification.pattern_file_path:
            pattern_instruction = f'Analyze the pattern from the source file: "{specification.pattern_file_path}".'
        elif specification.manual_pattern:
            pattern_instruction = f'Use the following JSON pattern directly: {specification.manual_pattern.model_dump_json()}'

        goal_prompt = f"""
            **MISSION BRIEFING:**
            You are a meticulous University Professor tasked with generating a question paper.

            Your output **must** be ONLY valid JSON, no markdown, no explanations, no extra text.
            Use this schema:
            {{
            "subject": "<subject>",
            "total_marks": <int>,
            "questions": [
                {{
                "question": "<text>",
                "marks": <int>
                }}
            ]
            }}

            Subject: {specification.subject}

            Additional instructions:
            - {pattern_instruction}
            - Use this syllabus context: {initial_context}
            """


        # --- Step 4: Run the Agent (No changes here) ---
        print("Running the agent with the master goal... This may take some time.")
        response: RunOutput = await agent.arun(goal_prompt)
        
        # --- Step 5: Process Final Response (No changes here) ---
        try:
            # Attempt to parse the agent's final output as JSON.
            final_paper = json.loads(response.content)
            print("Agent run completed successfully. Final paper parsed.")
            return final_paper
        except json.JSONDecodeError:
            print("Error: The agent's final output was not valid JSON.")
            return {
                "error": "Agent failed to produce a valid JSON output.",
                "raw_output": response.content
            }
    finally:
        # --- Step 6: Cleanup (No changes here) ---
        if rag_pipeline:
            print("Cleaning up RAG pipeline resources...")
            rag_pipeline.cleanup()