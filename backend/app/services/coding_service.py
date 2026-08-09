import logging

from sqlalchemy.orm import Session

from app import models
from app.services import chroma_service, ollama_service

logger = logging.getLogger(__name__)


def process_note(db: Session, note_content: str) -> tuple[models.Note, models.CodingSession]:
    note = models.Note(content=note_content)
    db.add(note)
    db.flush()

    extracted = ollama_service.extract_procedure_info(note_content)

    query = extracted.get("query") or _build_query(extracted) or note_content[:500]

    suggestions = chroma_service.search_codes(query)

    session = models.CodingSession(note_id=note.id, extracted_info=extracted)
    db.add(session)
    db.flush()

    for rank, s in enumerate(suggestions, start=1):
        db.add(
            models.SuggestedCode(
                session_id=session.id,
                code=s["code"],
                description=s["description"],
                similarity_score=s.get("rerank_score", s.get("cosine_similarity")),
                rank=rank,
            )
        )

    db.commit()
    db.refresh(note)
    db.refresh(session)
    return note, session


def _build_query(extracted: dict) -> str:
    parts = []
    for key in ("procedure_name", "body_site", "approach", "device"):
        val = extracted.get(key, "")
        if val and val.lower() not in ("none", "n/a", ""):
            parts.append(val)
    return " ".join(parts)
