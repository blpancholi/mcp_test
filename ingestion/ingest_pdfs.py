#!/usr/bin/env python3
"""
Ingest PDFs into ChromaDB collections (finance, medical, news).

Usage:
  python -m ingestion.ingest_pdfs --domain finance --path ./data/documents/finance
  python -m ingestion.ingest_pdfs --domain medical --path ./data/documents/medical
  python -m ingestion.ingest_pdfs --domain news --path ./data/documents/news

Or ingest a single PDF:
  python -m ingestion.ingest_pdfs --domain finance --file report.pdf
"""
import argparse
import uuid
from pathlib import Path

from pypdf import PdfReader

# Project root in path for config and hub
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CHUNK_OVERLAP, CHUNK_SIZE, DOMAINS
from hub.vector_store import get_collection


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks."""
    if not text or not text.strip():
        return []
    chunks = []
    start = 0
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def extract_text_from_pdf(path: Path) -> str:
    """Extract raw text from a PDF file."""
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n\n".join(parts)


def ingest_file(domain: str, file_path: Path, chunk_size: int, chunk_overlap: int) -> int:
    """Ingest one PDF into the domain collection. Returns number of chunks added."""
    if domain not in DOMAINS:
        raise ValueError(f"Domain must be one of {DOMAINS}, got {domain}")
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    if not chunks:
        return 0
    collection = get_collection(domain)
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": file_path.name} for _ in chunks]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def ingest_directory(domain: str, dir_path: Path, chunk_size: int, chunk_overlap: int) -> tuple[int, int]:
    """Ingest all PDFs in a directory. Returns (files_processed, total_chunks)."""
    total_chunks = 0
    count = 0
    for path in sorted(dir_path.glob("**/*.pdf")):
        try:
            n = ingest_file(domain, path, chunk_size, chunk_overlap)
            total_chunks += n
            count += 1
            print(f"  {path.name}: {n} chunks")
        except Exception as e:
            print(f"  {path.name}: ERROR {e}")
    return count, total_chunks


def main():
    parser = argparse.ArgumentParser(description="Ingest PDFs into ChromaDB for the Intelligence Hub")
    parser.add_argument("--domain", required=True, choices=DOMAINS, help="Target collection (finance, medical, news)")
    parser.add_argument("--path", type=Path, help="Directory containing PDFs to ingest")
    parser.add_argument("--file", type=Path, help="Single PDF file to ingest")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=CHUNK_OVERLAP, help="Overlap between chunks")
    args = parser.parse_args()

    if args.file:
        if not args.file.is_file():
            print(f"File not found: {args.file}")
            return 1
        n = ingest_file(args.domain, args.file, args.chunk_size, args.chunk_overlap)
        print(f"Ingested 1 file, {n} chunks into collection '{args.domain}'.")
        return 0

    if args.path:
        if not args.path.is_dir():
            print(f"Directory not found: {args.path}")
            return 1
        count, total = ingest_directory(args.domain, args.path, args.chunk_size, args.chunk_overlap)
        print(f"Ingested {count} files, {total} chunks into collection '{args.domain}'.")
        return 0

    print("Provide either --path <dir> or --file <path>.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
