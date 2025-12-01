import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
from pydantic import ValidationError

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

from Memory.schemas import MemoryExtraction  # optional, if you want strong typing

# Personality prompt templates
PERSONALITY_PROMPTS = {
    "normal": "You are a helpful AI assistant. Use the user's memory and respond naturally and clearly.",
    "calm_mentor": "You are a calm mentor. Respond in a patient, guiding, and encouraging manner. Use user's memory when relevant.",
    "witty_friend": "You are a witty friend. Keep the response casual, humorous, and relatable. Use user's memory naturally.",
    "therapist": "You are a supportive therapist. Empathize with user's emotions and give advice gently. Refer to user's memory if it helps."
}

def clean_model_text(raw_text: str) -> str:
    """
    Remove code blocks or extra markdown from model output.
    """
    import re
    cleaned = re.sub(r"```(?:json)?\n(.*?)```", r"\1", raw_text, flags=re.DOTALL)
    return cleaned.strip()


class PersonalityEngine:
    def __init__(self, user_memory: dict):
        """
        user_memory: dictionary containing preferences, emotional_patterns, and facts
        """
        self.memory = user_memory

    def memory_summary(self) -> str:
        """Convert user memory JSON into a textual summary for prompts."""
        summary = ""
        for pref in self.memory.get("preferences", []):
            summary += f"- Prefers {pref['value']} for {pref['category']}\n"
        for emo in self.memory.get("emotional_patterns", []):
            summary += f"- Often feels {emo['emotion']} when {emo['trigger']}\n"
        for fact in self.memory.get("facts", []):
            summary += f"- Fact: {fact['fact'] if 'fact' in fact else fact.get('key', '')}: {fact.get('value','')}\n"
        return summary.strip()

    def generate_prompt(self, user_message: str, style: str) -> str:
        if style not in PERSONALITY_PROMPTS:
            raise ValueError(f"Style '{style}' not supported. Choose from {list(PERSONALITY_PROMPTS.keys())}.")

        prompt = f"""
Personality: {PERSONALITY_PROMPTS[style]}

User Memory:
{self.memory_summary()}

User says: "{user_message}"
Respond naturally in the style above.
"""
        return prompt.strip()

    def respond(self, user_message: str, style: str) -> str:
        prompt = self.generate_prompt(user_message, style)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )

        return clean_model_text(response.text)


if __name__ == "__main__":
    MEMORY_PATH = r"D:\Companion_AI\Memory\memory_store.json"
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        user_memory = json.load(f)

    engine = PersonalityEngine(user_memory)

    user_input = "I'm struggling to stay consistent with my study routine."

    print("\n--- Responses with Personality ---\n")
    for style in PERSONALITY_PROMPTS.keys():
        response = engine.respond(user_input, style)
        print(f"Style: {style}\n{response}\n{'-'*60}\n")
