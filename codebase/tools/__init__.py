from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .clarify.tool import ask_user
from .list_topics.tool import list_topics
from .summarize_pages.tool import summarize_pages
from .search_materials.tool import search_materials
from .direct_to_btc.tool import direct_to_btc

TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "list_topics": list_topics,
    "summarize_pages": summarize_pages,
    "summary_pages": summarize_pages,
    "search_materials": search_materials,
    "direct_to_btc": direct_to_btc,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]
