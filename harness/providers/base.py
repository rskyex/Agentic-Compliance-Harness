"""The provider abstraction. Two stages: stated (text) and enacted (tool)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..types import EnactedCall, ToolSpec


@runtime_checkable
class LLMProvider(Protocol):
    """A swappable LLM backend.

    Implementations expose `provider_name` and `model` (recorded on every
    result for provenance) and two single-turn calls:

    - `stated`:  text-only. Ask whether the model will comply and what it will
                 do; return its free-text answer.
    - `enacted`: give the same prompt plus one mock tool and capture the actual
                 tool call. The call is *recorded, never executed*.
    """

    provider_name: str
    model: str

    def stated(self, system: str, user: str) -> str: ...

    def enacted(self, system: str, user: str, tool: ToolSpec) -> EnactedCall: ...
