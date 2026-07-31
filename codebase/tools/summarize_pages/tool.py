from __future__ import annotations

import re
from typing import Any
from tools.rag_knowledge import SLIDE_CHUNKS


def summarize_pages(from_page: int, to_page: int | None = None) -> dict[str, Any]:
    if to_page is None or to_page < from_page:
        to_page = from_page

    relevant = {}
    for label, content in SLIDE_CHUNKS.items():
        if "Slide:" in label:
            page_match = re.search(r'Page(\d+)', label)
            if page_match:
                p = int(page_match.group(1))
                if from_page <= p <= to_page:
                    relevant[label] = content[:1500]  # Trích đoạn ngắn để làm tóm tắt

    if not relevant:
        return {
            "tool": "summarize_pages",
            "error": f"Không tìm thấy trang slide trong khoảng {from_page} - {to_page}.",
            "pages": []
        }

    return {
        "tool": "summarize_pages",
        "pages": [{"source": k, "content": v} for k, v in relevant.items()]
    }
