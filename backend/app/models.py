from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship(
        "CodingSession", back_populates="note", cascade="all, delete-orphan"
    )


class CodingSession(Base):
    __tablename__ = "coding_sessions"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    extracted_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    note = relationship("Note", back_populates="sessions")
    suggestions = relationship(
        "SuggestedCode",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SuggestedCode.rank",
    )


class SuggestedCode(Base):
    __tablename__ = "suggested_codes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("coding_sessions.id"), nullable=False)
    code = Column(String(7), nullable=False)
    description = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=False)

    session = relationship("CodingSession", back_populates="suggestions")
