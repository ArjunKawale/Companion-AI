import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from .schemas import MemoryExtraction

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


EXTRACTION_PROMPT = """
You are a Memory Extraction Module.

You will receive ONE user message.

Extract ONLY:
1. User Preferences (likes, dislikes, habits)
2. User Emotional Patterns (common moods, triggers)
3. Long-term Facts Worth Remembering

Rules:
- Extract ONLY information suitable for long-term memory.
- Do not include short-term or situational info.
- If nothing found, return empty lists.
- Return JSON ONLY.

JSON schema:
{
  "preferences": [
    {"category": "", "value": "", "confidence": 0-1}
  ],
  "emotional_patterns": [
    {"emotion": "", "trigger": "", "confidence": 0-1}
  ],
  "facts": [
    {"key": "", "value": "", "confidence": 0-1}
  ]
}
"""


import re

def clean_model_json(raw_text: str) -> str:
    """
    Remove Markdown-style code blocks from model output.
    """
    # Remove ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?\n(.*?)```", r"\1", raw_text, flags=re.DOTALL)
    return cleaned.strip()


def extract_memory(message: str) -> MemoryExtraction:
    prompt = EXTRACTION_PROMPT + "\nUSER_MESSAGE:\n" + message

    response = client.models.generate_content(
        model="gemini-2.5-flash",  # updated model
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    raw = response.text
    cleaned = clean_model_json(raw)  # <-- strip code blocks

    try:
        parsed = MemoryExtraction.model_validate_json(cleaned)
    except ValidationError as e:
        print("Parsing error:", e)
        print("Raw output:", raw)
        raise e

    return parsed
