"""Anthropic backend (anthropic SDK), using native tool use for stage 2."""

from __future__ import annotations

from typing import Any

from ..types import EnactedCall, ToolSpec

_MAX_TOKENS = 1024


class AnthropicProvider:
    provider_name = "anthropic"

    def __init__(self, model: str) -> None:
        import anthropic  # imported lazily; needs ANTHROPIC_API_KEY in env

        self.model = model
        self._client = anthropic.Anthropic()

    def stated(self, system: str, user: str) -> str:
        return self.complete(system, user)

    def complete(self, system: str, user: str) -> str:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _join_text(resp.content)

    def enacted(self, system: str, user: str, tool: ToolSpec) -> EnactedCall:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=_MAX_TOKENS,
            system=system,
            tools=[
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.parameters,
                }
            ],
            tool_choice={"type": "auto"},
            messages=[{"role": "user", "content": user}],
        )
        text_parts: list[str] = []
        for block in resp.content:
            if block.type == "tool_use":
                return EnactedCall(
                    tool_name=block.name,
                    args=dict(block.input or {}),
                    raw_text=" ".join(text_parts).strip(),
                )
            if block.type == "text":
                text_parts.append(block.text)
        # No tool call: the model answered in text only.
        return EnactedCall(tool_name=None, args={}, raw_text=" ".join(text_parts).strip())


def _join_text(content: list[Any]) -> str:
    return "".join(b.text for b in content if getattr(b, "type", None) == "text").strip()
