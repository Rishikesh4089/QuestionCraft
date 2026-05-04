import json
import re

def extract_json_from_text(text: str) -> str:
    """
    Extracts JSON object from model output, even if wrapped in markdown or extra text.
    """
    # Clean code fences and markdown
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    # Try to locate JSON object boundaries
    match = re.search(r'({.*})', text, re.DOTALL)
    if match:
        text = match.group(1)
    return text

def safe_json_loads(text: str):
    """
    Safely loads JSON with minimal cleanup for minor model formatting quirks.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # attempt to fix trailing commas etc
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        try:
            return json.loads(cleaned)
        except Exception:
            raise e
