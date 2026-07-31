from __future__ import annotations

import json
import os
from typing import Any

from providers.base import ModelResponse, ToolCall


class GroqProvider:
    """Groq API provider with normalized tool_calls output (compatible with OpenAI format)."""

    def __init__(
        self,
        *,
        api_key_env: str = "GROQ_API_KEY",
        default_model: str = "llama3-8b-8192",
    ) -> None:
        self.api_key_env = api_key_env
        self.default_model = os.getenv("LLM_MODEL") or default_model

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("Install groq provider dependency first: pip install groq") from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        client = Groq(api_key=api_key)
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        import time
        import sys
        resp = None
        for attempt in range(4):
            try:
                resp = client.chat.completions.create(**kwargs)
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate_limit_exceeded" in err_str.lower() or "rate limit" in err_str.lower():
                    wait_time = (attempt + 1) * 6
                    try:
                        print(f"\n[WARNING] Hết hạn ngạch Groq (429/Rate Limit). Đang tự động thử lại sau {wait_time}s... (Lượt {attempt+1}/4)", file=sys.stderr)
                    except Exception:
                        pass
                    time.sleep(wait_time)
                    continue
                raise e
        else:
            raise RuntimeError("Hết lượt thử lại sau lỗi giới hạn ngạch Groq 429.")

        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            args = json.loads(call.function.arguments or "{}")
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)
