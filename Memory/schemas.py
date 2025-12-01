from pydantic import BaseModel
from typing import List, Optional


class UserPreference(BaseModel):
    category: str
    value: str
    confidence: float


class EmotionalPattern(BaseModel):
    emotion: str
    trigger: Optional[str]
    confidence: float


class Fact(BaseModel):
    key: str
    value: str
    confidence: float


class MemoryExtraction(BaseModel):
    preferences: List[UserPreference]
    emotional_patterns: List[EmotionalPattern]
    facts: List[Fact]
