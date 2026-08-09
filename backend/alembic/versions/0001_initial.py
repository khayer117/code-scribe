"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notes_id", "notes", ["id"], unique=False)

    op.create_table(
        "coding_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("note_id", sa.Integer(), nullable=False),
        sa.Column("extracted_info", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["note_id"], ["notes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_coding_sessions_id", "coding_sessions", ["id"], unique=False)

    op.create_table(
        "suggested_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(7), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["coding_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_suggested_codes_id", "suggested_codes", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_suggested_codes_id", table_name="suggested_codes")
    op.drop_table("suggested_codes")
    op.drop_index("ix_coding_sessions_id", table_name="coding_sessions")
    op.drop_table("coding_sessions")
    op.drop_index("ix_notes_id", table_name="notes")
    op.drop_table("notes")
