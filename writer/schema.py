from pydantic import BaseModel
from typing import Literal

class DocSection(BaseModel):
    section: Literal["installation", "getting_started", "features"]
    content: str
    revision_count: int = 0

class CriticFeedback(BaseModel):
    passed: bool
    notes: str
    