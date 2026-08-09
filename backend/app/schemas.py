from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    content: str


class SuggestedCodeOut(BaseModel):
    id: int
    code: str
    description: str
    similarity_score: Optional[float] = None
    rank: int

    model_config = ConfigDict(from_attributes=True)


class CodingSessionOut(BaseModel):
    id: int
    note_id: int
    extracted_info: Optional[Any] = None
    created_at: datetime
    suggestions: list[SuggestedCodeOut] = []

    model_config = ConfigDict(from_attributes=True)


class NoteOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    sessions: list[CodingSessionOut] = []

    model_config = ConfigDict(from_attributes=True)


class CodingResponse(BaseModel):
    note: NoteOut
    session: CodingSessionOut
