"""OpenAI-compatible backend (openai SDK).

Covers OpenAI directly and any OpenAI-compatible endpoint (e.g. OpenRouter)
by honoring OPENAI_BASE_URL. Stage 2 uses function calling.
"""

from __future__ import annotations

import json
import os

from ..types import EnactedCall, ToolSpec

_MAX_TOKENS = 1024


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, model: str) -> None:
        from openai import OpenAI  # lazy import; needs OPENAI_API_KEY in env

        self.model = model
        base_url = os.getenv("OPENAI_BASE_URL") or None
        self._client = OpenAI(base_url=base_url)

    def stated(self, system: str, user: str) -> str:
        return self.complete(system, user)

    def complete(self, system: str, user: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            max_tokens=_MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (resp.choices[0].message.content or "").strip()

    def enacted(self, system: str, user: str, tool: ToolSpec) -> EnactedCall:
        resp = self._client.chat.completions.create(
            model=self.model,
            max_tokens=_MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            ],
            tool_choice="auto",
        )
        message = resp.choices[0].message
        calls = message.tool_calls or []
        if calls:
            call = calls[0]
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"_raw_arguments": call.function.arguments}
            return EnactedCall(
                tool_name=call.function.name,
                args=args if isinstance(args, dict) else {"value": args},
                raw_text=(message.content or "").strip(),
            )
        return EnactedCall(tool_name=None, args={}, raw_text=(message.content or "").strip())
