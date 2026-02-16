"""Configuration for the Local Hybrid-Model Intelligence Hub."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Ollama (default: local Docker)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Router: fast classifier (≤3B)
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "llama3.2:3b")

# Domain -> expert model mapping (all ≤3B)
DOMAIN_MODELS = {
    "finance": os.getenv("MODEL_FINANCE", "qwen2.5:3b"),
    "medical": os.getenv("MODEL_MEDICAL", "llama3.2:3b"),
    "news": os.getenv("MODEL_NEWS", "llama3.2:3b"),
}

# Embedding model (local via Ollama)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

# ChromaDB persistence
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
CHROMA_PATH = DATA_DIR / "chroma_db"
PDF_INGEST_DIR = DATA_DIR / "documents"  # Optional: folder with PDFs to ingest

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))

# Supported domains (must match router output)
DOMAINS = ("finance", "medical", "news")
