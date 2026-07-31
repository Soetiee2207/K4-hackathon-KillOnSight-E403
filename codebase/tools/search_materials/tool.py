from __future__ import annotations

from typing import Any
from tools.rag_knowledge import retrieve_relevant_chunks


def search_materials(query: str) -> dict[str, Any]:
    result = retrieve_relevant_chunks(query, top_n=4)
    return {
        "tool": "search_materials",
        "query": query,
        "result": result
    }
