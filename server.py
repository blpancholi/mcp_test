"""
MCP Server: Local Hybrid-Model Intelligence Hub.

Exposes a single tool: query_intelligence_hub(query: str)
Run with: fastmcp run server.py   (or: python server.py)
"""
from fastmcp import FastMCP

from hub.orchestrator import query_intelligence_hub as _query_intelligence_hub

mcp = FastMCP("Local Intelligence Hub")


@mcp.tool
def query_intelligence_hub(query: str) -> str:
    """
    Query the local multi-domain intelligence hub. The system classifies your question
    into Finance, Medical, or News, retrieves relevant context from the local vector DB,
    and generates an answer using the best local model for that domain (e.g. Qwen for
    finance, Llama for medical/news). All processing stays on your machine.
    """
    return _query_intelligence_hub(query)


if __name__ == "__main__":
    mcp.run()
