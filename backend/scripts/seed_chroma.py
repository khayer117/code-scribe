"""Seed ChromaDB with all ICD-10-PCS codes.

Run from the backend directory:
    python scripts/seed_chroma.py

Downloads the ICD-10-PCS source file from CMS if not already present in
'source files/'. The download URL is configured via CMS_SOURCE_URL in .env.
"""

import os
import shutil
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.config import settings
from scripts.parse_pcs import ICD_FILE, parse_codes

BATCH_SIZE = 500


def ensure_source_file() -> None:
    if ICD_FILE.exists():
        print(f"Source file found: {ICD_FILE}")
        return

    print(f"Source file not found. Downloading from CMS...")
    print(f"  URL: {settings.CMS_SOURCE_URL}")

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "cms_icd10pcs.zip"

        urllib.request.urlretrieve(settings.CMS_SOURCE_URL, zip_path)
        print(f"  Downloaded to temp location")

        with zipfile.ZipFile(zip_path) as zf:
            matched = [n for n in zf.namelist() if n.lower().endswith(settings.ICD_SOURCE_FILENAME.lower())]
            if not matched:
                raise FileNotFoundError(
                    f"icd10pcs_codes_2027.txt not found in zip. Contents: {zf.namelist()}"
                )
            extracted = Path(zf.extract(matched[0], tmp))

        ICD_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(extracted), ICD_FILE)
        print(f"  Moved to: {ICD_FILE}")

def seed() -> None:
    ensure_source_file()
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
