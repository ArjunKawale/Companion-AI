# store.py
import json
from typing import List
from .schemas import MemoryExtraction

class MemoryStore:
    def __init__(self):
        self.memory_store = {
            "preferences": [],
            "emotional_patterns": [],
            "facts": []
        }

    def add_memory(self, extracted: MemoryExtraction):
        self.memory_store["preferences"].extend([
            {"category": p.category, "value": p.value, "confidence": p.confidence}
            for p in extracted.preferences
        ])
        self.memory_store["emotional_patterns"].extend([
            {"emotion": e.emotion, "trigger": e.trigger, "confidence": e.confidence}
            for e in extracted.emotional_patterns
        ])
        self.memory_store["facts"].extend([
            {"key": f.key, "value": f.value, "confidence": f.confidence}
            for f in extracted.facts
        ])

    def get_all(self):
        return self.memory_store

    def save_memory(self, path: str = "memory_store.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.memory_store, f, indent=4, ensure_ascii=False)
