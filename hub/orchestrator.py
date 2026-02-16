"""Router + RAG + expert model orchestration for the Intelligence Hub."""
import json
import re

from config import DOMAIN_MODELS, DOMAINS, ROUTER_MODEL
from hub.vector_store import retrieve


def _classify_domain(query: str) -> str:
    """Use the router model (Llama) to classify the query into finance, medical, or news."""
    import ollama
    prompt = f"""Classify the following user query into exactly one domain. Reply with a JSON object only, no other text.
Domains: {", ".join(DOMAINS)}

User query: {query}

Respond with JSON in this exact format: {{"domain": "<domain>"}}"""
    try:
        response = ollama.chat(
            model=ROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )
        text = (response.get("message") or {}).get("content", "") or ""
        # Extract JSON in case of markdown or extra text
        match = re.search(r'\{[^{}]*"domain"\s*:\s*"[^"]+"\s*\}', text)
        if match:
            data = json.loads(match.group())
            domain = (data.get("domain") or "").strip().lower()
            if domain in DOMAINS:
                return domain
        # Fallback: first domain
        return DOMAINS[0]
    except Exception:
        return DOMAINS[0]


def _generate_response(domain: str, query: str, context_chunks: list[str]) -> str:
    """Call the domain-specific expert model with retrieved context."""
    import ollama
    model = DOMAIN_MODELS.get(domain) or DOMAIN_MODELS["news"]
    context = "\n\n".join(context_chunks) if context_chunks else "(No relevant documents found.)"
    prompt = f"""Use the following context to answer the user question. If the context does not contain enough information, say so and answer from general knowledge.

Context:
{context}

User question: {query}

Answer concisely and accurately."""
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.get("message") or {}).get("content", "No response generated.")
    except Exception as e:
        return f"Error calling expert model: {e}"


def query_intelligence_hub(query: str) -> str:
    """
    Full pipeline: classify domain -> retrieve from vector DB -> generate with expert model.
    """
    domain = _classify_domain(query)
    chunks = retrieve(domain, query)
    answer = _generate_response(domain, query, chunks)
    return answer
