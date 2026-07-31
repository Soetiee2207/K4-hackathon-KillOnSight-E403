from __future__ import annotations

from typing import Any


def direct_to_btc(reason: str = "") -> dict[str, Any]:
    return {
        "tool": "direct_to_btc",
        "reason": reason,
        "message": (
            "Tôi không thể cung cấp thông tin này để tránh sai sót. "
            "Bạn vui lòng kiểm tra Discord của lớp học hoặc liên hệ trực tiếp Ban Tổ Chức (BTC) để có thông tin chính xác nhất."
        )
    }
