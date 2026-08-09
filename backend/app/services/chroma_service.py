import logging

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import CrossEncoder

from app.config import settings

logger = logging.getLogger(__name__)

_chroma_client: chromadb.PersistentClient | None = None
_collection = None
_cross_encoder: CrossEncoder | None = None


def _client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    return _chroma_client


def _get_collection():
    global _collection
    if _collection is None:
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        _collection = _client().get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _reranker() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _cross_encoder


def get_collection_count() -> int:
    try:
        return _get_collection().count()
    except Exception:
        return 0


def search_codes(query: str, n_results: int | None = None, rerank_candidates: int | None = None) -> list[dict]:
    if n_results is None:
        n_results = settings.TOP_K_RESULTS
    if rerank_candidates is None:
        rerank_candidates = settings.RERANK_CANDIDATES

    collection = _get_collection()
    total = collection.count()
    if total == 0:
        return []

    fetch_n = min(max(rerank_candidates, n_results), total)

    results = collection.query(
        query_texts=[query],
        n_results=fetch_n,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    candidates = [
        {
            "code": m.get("code", ""),
            "description": doc,
            "cosine_similarity": 1.0 - dist,
        }
        for doc, m, dist in zip(docs, metas, distances)
    ]

    if len(candidates) > 1:
        try:
            pairs = [[query, c["description"]] for c in candidates]
            scores = _reranker().predict(pairs)
            for i, score in enumerate(scores):
                candidates[i]["rerank_score"] = float(score)
            candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        except Exception as exc:
            logger.warning("Cross-encoder reranking failed, falling back to cosine: %s", exc)
            candidates.sort(key=lambda x: x["cosine_similarity"], reverse=True)

    top = candidates[:n_results]
    for candidate in top:
        candidate.setdefault("rerank_score", candidate["cosine_similarity"])
    return top
