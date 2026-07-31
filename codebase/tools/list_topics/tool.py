from __future__ import annotations

from typing import Any
from tools.rag_knowledge import SLIDE_CHUNKS


def list_topics() -> dict[str, Any]:
    topics = [
        "Day 1 Slide: Khám phá vấn đề & JTBD (Tr.4-14)",
        "Day 2 Slide: Thiết kế sản phẩm AI & HAX (Tr.15-33)",
        "Day 2 Slide: Đo lường & Golden Set (Tr.34-40)",
        "Day 2 Slide: Ràng buộc & Rủi ro bảo mật (Tr.8-11)",
        "Transcripts bài giảng Day01 - Day06",
        "Quy định & Tài liệu Hackathon (01-de-bai.md, 02-guide.md, 03-template-ai-spec.md, 04-rubric.md)"
    ]
    return {
        "tool": "list_topics",
        "topics": topics,
        "total_chunks": len(SLIDE_CHUNKS)
    }
