from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.services import chroma_service, coding_service

router = APIRouter()


@router.post("/notes", response_model=schemas.CodingResponse)
def create_note(note_in: schemas.NoteCreate, db: Session = Depends(get_db)):
    if not note_in.content.strip():
        raise HTTPException(status_code=400, detail="Note content cannot be empty")

    if chroma_service.get_collection_count() == 0:
        raise HTTPException(
            status_code=503,
            detail="ICD-10-PCS codes not loaded. Run: python scripts/seed_chroma.py",
        )

    try:
        note, session = coding_service.process_note(db, note_in.content)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return schemas.CodingResponse(
        note=schemas.NoteOut.model_validate(note),
        session=schemas.CodingSessionOut.model_validate(session),
    )


@router.get("/notes", response_model=List[schemas.NoteOut])
def list_notes(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(models.Note)
        .order_by(models.Note.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/notes/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/health")
def health_check():
    count = chroma_service.get_collection_count()
    return {"status": "ok", "chroma_codes_loaded": count, "ready": count > 0}
