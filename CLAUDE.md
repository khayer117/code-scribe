# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project layout

```
source files/          # Raw ICD-10-PCS 2027 data (read-only, never modify)
backend/               # FastAPI app — run all Python commands from here
frontend/              # React + Vite app
```

## Source data setup

The source file (`icd10pcs_codes_2027.txt`) is downloaded automatically from CMS when `seed_chroma.py` runs. If the file already exists in `source files/`, the download is skipped. The URL is configured via `CMS_SOURCE_URL` in `backend/.env` (or `app/config.py`).

## Common commands

All backend commands must be run from `backend/`:

```bash
# First-time setup
powershell -ExecutionPolicy Bypass # Windows PowerShell
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_chroma.py   # one-time; downloads source from CMS + embeds ~78k codes (~30-60 min on CPU)

# Start backend (requires Ollama running separately)
uvicorn app.main:app --reload

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Re-seed ChromaDB (idempotent — drops and recreates the collection)
python scripts/seed_chroma.py

# Parse codes only (no ChromaDB write)
python scripts/parse_pcs.py
```

Frontend (`frontend/`):

```bash
npm install
npm run dev      # http://localhost:5173
npm run build
```

Ollama (separate process):

```bash
ollama serve
ollama pull llama3.1:8b
```

Health check after startup: `GET http://localhost:8000/api/health` — `ready: true` means ChromaDB is seeded.

## Architecture

### Request pipeline

`POST /api/notes` triggers a synchronous three-stage pipeline in `coding_service.process_note`:

1. **Extraction** (`ollama_service.py`) — sends the note to Ollama with a structured JSON prompt; returns fields `procedure_name`, `body_site`, `approach`, `device`, `qualifier`, `query`. The `query` field is used directly for vector search; if absent, the other fields are concatenated by `_build_query`.

2. **Vector search + reranking** (`chroma_service.py`) — queries ChromaDB for `RERANK_CANDIDATES` (default 20) cosine-nearest descriptions, then reranks them with `cross-encoder/ms-marco-MiniLM-L-6-v2` and returns the top `TOP_K_RESULTS` (default 10). If the cross-encoder fails it falls back silently to cosine order.

3. **Persistence** — writes `Note → CodingSession → SuggestedCode[]` to SQLite in a single transaction. `similarity_score` on each `SuggestedCode` stores the cross-encoder logit (not a bounded [0,1] value).

### ChromaDB singleton pattern

`chroma_service.py` holds three module-level globals (`_chroma_client`, `_collection`, `_cross_encoder`) initialized lazily on first access. The `SentenceTransformerEmbeddingFunction` is attached to the collection at creation time, so ChromaDB handles embedding automatically on both insert and query — raw embeddings are never computed manually in application code.

The collection uses `hnsw:space: cosine`. Document text is the full ICD-10-PCS description; metadata carries only `{"code": "XXXXXXX"}`.

### Database (SQLAlchemy sync)

**Do not switch to async SQLAlchemy** — the app is intentionally sync. `engine` uses `check_same_thread=False` for SQLite. The ORM layer is:

```
Note  1──*  CodingSession  1──*  SuggestedCode
```

`CodingSession.extracted_info` is a JSON column storing the raw Ollama response dict. `SuggestedCode` rows are ordered by `rank` at the relationship level.

Schema changes require an Alembic migration — `Base.metadata.create_all` in `main.py` is a safety net for the initial table creation only, not for subsequent migrations.

### Configuration

All tunables live in `backend/.env` and are typed in `app/config.py` via `pydantic-settings`. The `Settings` singleton is imported as `from app.config import settings` everywhere. Adding a new setting requires only a new field on `Settings` — no other wiring needed.

| Key | Purpose |
|---|---|
| `OLLAMA_MODEL` | Any model available in Ollama |
| `OLLAMA_TIMEOUT` | Seconds; increase for slow hardware |
| `RERANK_CANDIDATES` | Candidates fetched before reranking (≥ `TOP_K_RESULTS`) |
| `TOP_K_RESULTS` | Final results returned to the UI |
| `CHROMA_DB_PATH` | Persistent directory for ChromaDB; relative to `backend/` |

### Source data

- Flat code file: `source files/icd10pcs_codes_2027.txt` — one code per line, format `CCCCCCC Description text`
- XML tables/index/definitions: `source files/2027-code-tables-and-index/` — not currently used by the app
- `scripts/parse_pcs.py` owns the parsing logic; `scripts/seed_chroma.py` imports from it

### Frontend

Single-page React app with two routes (`/` and `/history`). API calls go through `src/api/client.js` (Axios, 3-minute timeout, baseURL `/api`). Vite proxies `/api` → `http://localhost:8000` in dev. The response from `POST /api/notes` is `CodingResponse` which carries both the saved `note` and the `session` with inline `suggestions` — the frontend does not make a second request.
