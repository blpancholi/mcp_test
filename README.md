# Local Hybrid-Model Intelligence Hub (MCP)

A **Multi-Domain Private Intelligence Hub** that routes user queries to the best local Ollama model and uses a local vector DB (ChromaDB) for RAG. Everything runs on your machine.

## Architecture

All language models are **≤3B** for low resource use. Embeddings use **nomic-embed-text**.

1. **Router** (`llama3.2:3b`) – Classifies the query into **Finance**, **Medical**, or **News** and returns a domain label.
2. **Vector DB** (ChromaDB) – Per-domain collections; embeddings via **nomic-embed-text** (Ollama). Retrieves relevant chunks for the query.
3. **Expert models** – Domain-specific models (all ≤3B) answer using retrieved context:
   - **Finance** → `qwen2.5:3b`
   - **Medical** → `llama3.2:3b`
   - **News** → `llama3.2:3b`

## Prerequisites

- **Ollama** running (e.g. in Docker) with these models (all ≤3B except the embedding model):
  - Router: `llama3.2:3b`
  - Embeddings: `nomic-embed-text`
  - Experts: `qwen2.5:3b`, `llama3.2:3b`
- Python 3.10+

## Setup

```bash
# Clone or cd into project
cd MCP_TEST

# Create venv and install
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy env and edit if needed (Ollama host, model names)
cp .env.example .env

# Ensure required Ollama models are pulled (checks and pulls only missing ones)
OLLAMA_HOST=http://localhost:11434 python scripts/ensure_ollama_models.py
```

## Ensuring Ollama models (≤3B)

The project is configured to use only **3B or smaller** models. To check which models are installed and pull any that are missing:

```bash
# With Ollama on localhost
python scripts/ensure_ollama_models.py

# With Ollama in Docker or on another host
OLLAMA_HOST=http://localhost:11434 python scripts/ensure_ollama_models.py
```

Required models:

| Model | Role |
|-------|------|
| `llama3.2:3b` | Router + Medical + News expert |
| `qwen2.5:3b` | Finance expert |
| `nomic-embed-text` | Embeddings for ChromaDB |

## Configuration

Edit `.env` (or set environment variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API URL (use `http://host.docker.internal:11434` if MCP runs in Docker) |
| `ROUTER_MODEL` | `llama3.2:3b` | Model used for domain classification (≤3B) |
| `MODEL_FINANCE` | `qwen2.5:3b` | Expert for finance (≤3B) |
| `MODEL_MEDICAL` | `llama3.2:3b` | Expert for medical (≤3B) |
| `MODEL_NEWS` | `llama3.2:3b` | Expert for news (≤3B) |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model for ChromaDB |
| `DATA_DIR` | `./data` | Base path; ChromaDB at `DATA_DIR/chroma_db` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 1000 / 200 | PDF chunking for ingestion |
| `TOP_K_RETRIEVAL` | 5 | Number of chunks to retrieve per query |

## Sample documents (PDFs)

You can generate sample PDFs for all three domains so the hub has data to answer from:

```bash
python scripts/generate_sample_documents.py
```

This creates PDFs under `data/documents/`:

| Domain   | Files | Content |
|----------|--------|---------|
| **Finance** | `income_tax_qa.pdf`, `gst_qa.pdf` | Income tax (slabs, TDS, deductions) and GST (registration, rates, ITC, returns) Q&A |
| **Medical** | `common_diseases_cause_cure.pdf`, `sample_prescriptions.pdf` | Common diseases (cause & treatment): hypertension, diabetes, cold, gastritis, migraine; sample prescriptions (URTI, hypertension, diabetes, gastritis) |
| **News**  | `sports_news.pdf`, `politics_news.pdf`, `movie_news.pdf` | Sample articles: sports (cricket, football, Olympics), politics (budget, elections, cabinet), movies (box office, director, streaming) |

After generating, ingest them (see below). You can edit `scripts/generate_sample_documents.py` to change or add content and re-run.

## Ingesting PDFs

Put PDFs in domain-specific folders (or use a single file), then run:

```bash
# Ingest a directory of PDFs into the finance collection
python -m ingestion.ingest_pdfs --domain finance --path ./data/documents/finance

# Ingest a directory into medical
python -m ingestion.ingest_pdfs --domain medical --path ./data/documents/medical

# Ingest a directory into news
python -m ingestion.ingest_pdfs --domain news --path ./data/documents/news

```

Collections are created automatically. Use the same `DATA_DIR` (and thus same ChromaDB path) as when running the MCP server.

## Running the MCP Server

**Stdio (for Cursor / MCP clients):**

```bash
fastmcp run server.py
```

Or:

```bash
python server.py
```

**HTTP (optional):**

Edit `server.py` and use:

```python
if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
```

Then point your MCP client to `http://127.0.0.1:8000/mcp`.

**Cursor:** Add to `.cursor/mcp.json` (or Cursor MCP settings) to use the tool from Cursor:

```json
{
  "mcpServers": {
    "intelligence-hub": {
      "command": "python",
      "args": ["/absolute/path/to/MCP_TEST/server.py"],
      "cwd": "/absolute/path/to/MCP_TEST",
      "env": {}
    }
  }
}
```

Use the absolute path to your project and ensure the venv is activated (or use the venv’s `python` in `command`).

## MCP Tool

The server exposes a single tool:

- **`query_intelligence_hub(query: str)`**  
  Runs the full pipeline: classify domain → retrieve from ChromaDB → generate answer with the domain’s expert model. Returns the model’s response as a string.

Example (from an MCP client): call `query_intelligence_hub` with `query = "What is the revenue growth for Tesla in Q3?"`. The router will classify as `finance`, retrieval will run on the `finance` collection, and the answer will be generated with `qwen2.5:3b` (or your configured finance model).

## Testing with curl

The MCP server uses **stdio** by default (for Cursor), so it has no HTTP endpoint. To test with **curl**, run the small test API in another terminal:

```bash
python run_test_api.py
```

This starts an HTTP server at **http://127.0.0.1:8765** with one route: **POST /query**. Then run:

**1. Health check**
```bash
curl -s http://127.0.0.1:8765/health
```

**2. Finance (Income Tax / GST)** – should route to finance and use the finance collection + model:
```bash
curl -s -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the basic exemption limit for income tax?"}'
```

```bash
curl -s -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Input Tax Credit in GST?"}'
```

**3. Medical** – should route to medical and use the medical collection + model:
```bash
curl -s -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the treatment for hypertension?"}'
```

**4. News** – should route to news and use the news collection + model:
```bash
curl -s -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Any cricket or Olympics news?"}'
```

Each response is JSON: `{"query": "...", "answer": "..."}`. Ensure Ollama is running and you have ingested the sample PDFs so the RAG has context.

## Project Layout

```
MCP_TEST/
├── config.py           # Settings (Ollama, models, paths, RAG)
├── server.py           # FastMCP server; exposes query_intelligence_hub
├── run_test_api.py     # Optional: HTTP API for curl testing (POST /query)
├── hub/
│   ├── embeddings.py   # Ollama embedding function for ChromaDB
│   ├── vector_store.py # ChromaDB collections and retrieval
│   └── orchestrator.py # Router + retrieve + expert pipeline
├── ingestion/
│   └── ingest_pdfs.py  # PDF → chunks → ChromaDB (per domain)
├── scripts/
│   ├── ensure_ollama_models.py     # Check and pull missing Ollama models (≤3B)
│   └── generate_sample_documents.py  # Generate sample PDFs for finance, medical, news
├── data/               # Created at runtime (DATA_DIR)
│   ├── chroma_db/      # ChromaDB persistence
│   └── documents/      # Optional: place PDFs here
├── requirements.txt
├── .env.example
└── README.md
```

## Privacy and Customization

- **Privacy:** All inference and data stay local (Ollama + ChromaDB).
- **Fine-tuning:** Point `MODEL_MEDICAL` (or others) to your own Ollama model name (must be ≤3B if you want to keep the 3B cap).
- **Router:** You can switch `ROUTER_MODEL` to a smaller/faster model if needed; keep the prompt in `hub/orchestrator.py` so it still returns `{"domain": "finance"|"medical"|"news"}`.

## Troubleshooting

- **Connection refused to Ollama** – Ensure Ollama is running and `OLLAMA_HOST` is correct (e.g. `http://host.docker.internal:11434` from another container).
- **Model not found** – Run `python scripts/ensure_ollama_models.py` to pull missing models, or manually: `ollama pull nomic-embed-text`, `ollama pull llama3.2:3b`, `ollama pull qwen2.5:3b`.
- **Empty or irrelevant answers** – Ingest more PDFs for that domain and/or increase `TOP_K_RETRIEVAL` or adjust chunk size in ingestion.
