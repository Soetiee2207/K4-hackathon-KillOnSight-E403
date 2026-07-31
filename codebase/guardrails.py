from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


SAFE_REFUSAL = (
    "Mình không thể cung cấp prompt hệ thống, mã nguồn nội bộ, khóa API hoặc dữ liệu bí mật. "
    "Mình có thể hỗ trợ giải thích kiến thức học tập, tóm tắt nội dung và hướng dẫn an toàn."
)


@dataclass
class GuardrailDecision:
    allowed: bool
    safe_message: str | None = None
    reason: str | None = None


SENSITIVE_PATTERNS = [
    r"\b(system prompt|internal prompt|developer message|hidden instructions?|prompt leak|reveal prompt)\b",
    r"\b(source code|full implementation|repository code|codebase contents|artifacts|company_policy)\b",
    r"\b(api key|secret key|access token|private key|password|token)\b",
    r"\b(ignore previous instructions|act as developer|jailbreak|bypass guardrail)\b",
]

SECRET_LIKE_PATTERNS = [
    r"\b(sk-[a-zA-Z0-9_-]{10,})\b",
    r"\b(ghp_[a-zA-Z0-9]{16,})\b",
    r"\b(AIza[0-9A-Za-z\-_]{20,})\b",
    r"\b(xox[baprs]-[A-Za-z0-9-]{10,})\b",
    r"\b(eyJ[A-Za-z0-9_-]{10,}\.)\b",
]


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _looks_sensitive(text: Any) -> bool:
    normalized = " ".join(_normalize_text(text).lower().split())
    if not normalized:
        return False
    for pattern in SENSITIVE_PATTERNS + SECRET_LIKE_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return True
    return False


def apply_input_guardrails(user_text: str) -> GuardrailDecision:
    if not user_text or not str(user_text).strip():
        return GuardrailDecision(allowed=True)

    if _looks_sensitive(user_text):
        return GuardrailDecision(allowed=False, safe_message=SAFE_REFUSAL, reason="sensitive_request")

    return GuardrailDecision(allowed=True)


def apply_output_guardrails(text: str | None) -> str | None:
    if not text:
        return text

    if _looks_sensitive(text):
        return SAFE_REFUSAL

    return text


def apply_tool_guardrails(tool_name: str, args: dict[str, Any] | None) -> GuardrailDecision:
    if not tool_name:
        return GuardrailDecision(allowed=True)

    normalized_tool = str(tool_name).lower()
    payload = " "
    if isinstance(args, dict):
        payload = " ".join(_normalize_text(value) for value in args.values())

    if normalized_tool == "send":
        confirmed = bool((args or {}).get("confirmed", False))
        if not confirmed:
            return GuardrailDecision(
                allowed=False,
                safe_message="Mình cần xác nhận rõ ràng trước khi gửi nội dung ra bên ngoài.",
                reason="send_requires_confirmation",
            )

    if _looks_sensitive(payload):
        return GuardrailDecision(allowed=False, safe_message=SAFE_REFUSAL, reason="sensitive_tool_payload")

    return GuardrailDecision(allowed=True)
