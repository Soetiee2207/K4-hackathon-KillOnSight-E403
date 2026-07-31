from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from guardrails import apply_input_guardrails, apply_output_guardrails, apply_tool_guardrails
from providers.base import Provider, ToolCall
from tools import TOOL_FUNCTIONS


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class TutorAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model

    def run(self, user_messages: list[dict[str, str]], *, tool_choice: Any | None = None) -> AgentRun:
        for message in user_messages:
            if message.get("role") != "user":
                continue
            decision = apply_input_guardrails(message.get("content", ""))
            if not decision.allowed:
                return AgentRun(text=decision.safe_message, tool_calls=[], tool_results=[])

        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        safe_text = apply_output_guardrails(response.text)
        results: list[dict[str, Any]] = []
        for call in response.tool_calls:
            guardrail_decision = apply_tool_guardrails(call.name, call.args)
            if not guardrail_decision.allowed:
                results.append({"tool": call.name, "args": call.args, "result": {"blocked": True, "message": guardrail_decision.safe_message}})
                continue

            func = TOOL_FUNCTIONS.get(call.name)
            if not func:
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            try:
                result = func(**call.args)
            except Exception as exc:
                result = {"error": type(exc).__name__, "message": str(exc)}
            results.append({"tool": call.name, "args": call.args, "result": result})
        return AgentRun(text=safe_text, tool_calls=response.tool_calls, tool_results=results)
