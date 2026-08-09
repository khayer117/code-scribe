"""Seed ChromaDB with all ICD-10-PCS codes.

Run from the backend directory:
    python scripts/seed_chroma.py

Expects .env in the backend directory with CHROMA_DB_PATH, EMBEDDING_MODEL,
and CHROMA_COLLECTION set (or uses defaults).
"""

import os
import sys
import time

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.config import settings
from scripts.parse_pcs import parse_codes

BATCH_SIZE = 500


def seed() -> None:
    print("Parsing ICD-10-PCS codes...")
    codes = parse_codes()
    print(f"  Found {len(codes):,} codes")

    print(f"\nConnecting to ChromaDB at: {settings.CHROMA_DB_PATH}")
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

    print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )

    # Drop and recreate so re-runs are idempotent
    try:
        client.delete_collection(settings.CHROMA_COLLECTION)
        print("  Deleted existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name=settings.CHROMA_COLLECTION,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    total = len(codes)
    num_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nInserting {total:,} codes in {num_batches} batches of {BATCH_SIZE}…")
    t0 = time.time()

    for batch_idx, start in enumerate(range(0, total, BATCH_SIZE), 1):
        batch = codes[start : start + BATCH_SIZE]
        collection.add(
            ids=[c["code"] for c in batch],
            documents=[c["description"] for c in batch],
            metadatas=[{"code": c["code"]} for c in batch],
        )
        elapsed = time.time() - t0
        pct = (start + len(batch)) / total * 100
        print(
            f"  [{batch_idx}/{num_batches}] {start + len(batch):,}/{total:,}  "
            f"({pct:.1f}%)  {elapsed:.1f}s",
            end="\r",
        )

    print(f"\nDone. {collection.count():,} codes in ChromaDB  "
          f"(took {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    seed()
