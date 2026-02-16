"""ChromaDB vector store with per-domain collections and Ollama embeddings."""
from pathlib import Path
from typing import Optional

import chromadb

from config import CHROMA_PATH, EMBEDDING_MODEL, OLLAMA_HOST, TOP_K_RETRIEVAL
from hub.embeddings import OllamaEmbeddingFunction

_embedding_fn: Optional[OllamaEmbeddingFunction] = None
_chroma_client: Optional[chromadb.PersistentClient] = None


def _get_embedding_fn() -> OllamaEmbeddingFunction:
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = OllamaEmbeddingFunction(model=EMBEDDING_MODEL, host=OLLAMA_HOST)
    return _embedding_fn


def _get_client() -> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _chroma_client


def get_collection(domain: str):
    """Get or create a ChromaDB collection for the given domain."""
    client = _get_client()
    return client.get_or_create_collection(
        name=domain,
        metadata={"description": f"Documents for domain: {domain}"},
        embedding_function=_get_embedding_fn(),
    )


def get_vector_store():
    """Return the ChromaDB client (for ingestion). Use get_collection(domain) for retrieval."""
    return _get_client()


def retrieve(domain: str, query: str, top_k: Optional[int] = None) -> list[str]:
    """Retrieve top-k relevant chunks from the domain collection."""
    k = top_k or TOP_K_RETRIEVAL
    coll = get_collection(domain)
    results = coll.query(query_texts=[query], n_results=k)
    if not results or not results.get("documents"):
        return []
    return results["documents"][0] or []
