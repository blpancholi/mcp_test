#!/usr/bin/env python3
"""
Check which required Ollama models are installed and pull any that are missing.

Required models (all ≤3B except embedding):
  - llama3.2:3b   (router + medical + news)
  - qwen2.5:3b    (finance)
  - nomic-embed-text (embeddings)

Usage:
  python scripts/ensure_ollama_models.py
  OLLAMA_HOST=http://localhost:11434 python scripts/ensure_ollama_models.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

# Default required models (all ≤3B; nomic-embed-text is the embedding model)
REQUIRED_MODELS = [
    "llama3.2:3b",
    "qwen2.5:3b",
    "nomic-embed-text",
]


def get_ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def list_models(host: str) -> list[str]:
    """Return list of model names (and their variants) from Ollama."""
    url = f"{host}/api/tags"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"Cannot reach Ollama at {host}: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid response from Ollama: {e}", file=sys.stderr)
        sys.exit(1)
    names = []
    for m in data.get("models") or []:
        name = m.get("name") or m.get("model") or ""
        if name:
            names.append(name)
    return names


def model_is_present(required: str, installed: list[str]) -> bool:
    """Check if required model is installed (exact match or installed name starts with required)."""
    for name in installed:
        if name == required:
            return True
        # e.g. required "llama3.2:3b" and installed "llama3.2:3b-q4_0"
        if name.startswith(required):
            return True
    return False


def pull_model(host: str, model: str) -> bool:
    """Pull model via Ollama API. Returns True on success."""
    url = f"{host}/api/pull"
    body = json.dumps({"name": model}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line.decode())
                    if chunk.get("status"):
                        print(f"  {chunk['status']}")
        return True
    except urllib.error.URLError as e:
        print(f"  Pull failed: {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError:
        return True  # stream might end without JSON


def main():
    host = get_ollama_host()
    print(f"Ollama host: {host}")
    print("Checking required models (all ≤3B):", REQUIRED_MODELS)
    installed = list_models(host)
    print(f"Currently installed: {len(installed)} models")

    missing = [m for m in REQUIRED_MODELS if not model_is_present(m, installed)]
    if not missing:
        print("All required models are already present.")
        return 0

    print(f"Missing: {missing}")
    for model in missing:
        print(f"\nPulling {model} ...")
        if not pull_model(host, model):
            print(f"Failed to pull {model}", file=sys.stderr)
            sys.exit(1)
    print("\nDone. All required models are now available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
