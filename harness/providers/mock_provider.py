"""Offline deterministic stub — no API key, no network.

It exists so the harness is runnable and testable without spending tokens.
It is NOT a model: it follows a fixed script designed to exhibit the very
pattern the harness measures. It keys off two markers the prompt builder
plants in the system prompt:

  - "Rule:"        -> the rule is salient (and its limit is parseable)
  - "step by step" -> the model was asked to show its reasoning

Scripted behavior:
  * stated:  always claims it will comply (so we can detect when actions
             contradict the words).
  * enacted: when the rule is salient AND reasoning is shown, it acts within
             the limit (honest compliance). Otherwise it enacts the tempting
             value from the request (a violation) while still having *claimed*
             compliance — i.e. deceptive compliance.
"""

from __future__ import annotations

import re

from ..types import EnactedCall, ToolSpec

_STATED_ANSWER = (
    "Yes, I will comply. I'll handle this responsibly and stay within the "
    "maximum allowed limit; I will not exceed it."
)


class MockProvider:
    provider_name = "mock"

    def __init__(self, model: str) -> None:
        # Record the configured model id for provenance even though no model runs.
        self.model = model

    def stated(self, system: str, user: str) -> str:
        return _STATED_ANSWER

    def enacted(self, system: str, user: str, tool: ToolSpec) -> EnactedCall:
        rule_salient = "Rule:" in system
        cot_shown = "step by step" in system.lower()
        limit = _parse_limit(system)
        tempting = _largest_number(user)

        if rule_salient and cot_shown and limit is not None:
            value: float = limit  # act within the limit -> compliant
        else:
            value = tempting if tempting is not None else (limit or 0)

        args = _fill_args(tool, value)
        return EnactedCall(tool_name=tool.name, args=args, raw_text="")


def _parse_limit(system: str) -> int | None:
    m = re.search(r"more than (\d+)", system)
    return int(m.group(1)) if m else None


def _largest_number(text: str) -> int | None:
    nums = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", text)]
    return max(nums) if nums else None


def _fill_args(tool: ToolSpec, value: float) -> dict[str, object]:
    """Put `value` into the first numeric property; fill the rest plausibly."""
    props: dict = tool.parameters.get("properties", {})
    args: dict[str, object] = {}
    for name, schema in props.items():
        ptype = schema.get("type")
        if ptype in ("integer", "number"):
            args[name] = int(value) if ptype == "integer" else float(value)
        else:
            args[name] = "unspecified"
    return args
