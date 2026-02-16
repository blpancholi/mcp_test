"""Ollama-based embedding function for ChromaDB (nomic-embed-text)."""
import os
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

# Optional: force Ollama host from config so it's set before ollama client is used
def _ensure_ollama_host():
    from config import OLLAMA_HOST
    if OLLAMA_HOST:
        os.environ["OLLAMA_HOST"] = OLLAMA_HOST


class OllamaEmbeddingFunction(EmbeddingFunction[Documents]):
    """ChromaDB embedding function using Ollama (e.g. nomic-embed-text)."""

    def __init__(self, model: str = "nomic-embed-text", host: str | None = None):
        _ensure_ollama_host()
        if host:
            os.environ["OLLAMA_HOST"] = host
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        import ollama
        if not input:
            return []
        # Ollama embed: input can be str or list of str; returns embeddings list
        raw = ollama.embed(model=self.model, input=input)
        emb = raw["embeddings"]
        if not emb:
            return []
        # Ensure we always return list[list[float]]
        if isinstance(emb[0], list):
            return emb
        return [emb]
