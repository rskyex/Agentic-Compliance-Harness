"""Shared, type-hinted data structures for the harness."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# A per-scenario action checker: given the enacted tool name (or None if the
# model called no tool) and the call arguments, decide whether the action
# complied with the scenario's rule and explain why.
ActionChecker = Callable[[Optional[str], dict[str, Any]], "CheckResult"]

# A per-scenario heuristic over the stage-1 free text: did the model's *words*
# claim it would comply? Used only to label stated-vs-enacted consistency.
StatedIntent = Callable[[str], bool]


@dataclass(frozen=True)
class ToolSpec:
    """A mock tool the agent may call. Recorded, never executed.

    `parameters` is a JSON-Schema object, shared verbatim by both providers
    (Anthropic `input_schema`, OpenAI function `parameters`).
    """

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class Scenario:
    """A rule + a tempting request + a mock tool + how to grade the action."""

    id: str
    title: str
    rule_text: str
    user_request: str
    tool: ToolSpec
    check_action: ActionChecker
    stated_claims_compliance: StatedIntent


@dataclass(frozen=True)
class Condition:
    """One experimental cell. The 2x2 set is built in `conditions()` below."""

    name: str
    rule_salient: bool  # is the rule stated in the system prompt?
    show_cot: bool  # is the model asked to show chain-of-thought?


@dataclass(frozen=True)
class CheckResult:
    """Output of an action checker."""

    compliant: bool
    reason: str


@dataclass(frozen=True)
class EnactedCall:
    """What the model actually did in stage 2 (the tool call), recorded raw."""

    tool_name: Optional[str]
    args: dict[str, Any]
    raw_text: str = ""  # any free text the model emitted alongside the call


@dataclass
class RunRecord:
    """One row of results/runs.jsonl."""

    scenario_id: str
    condition: str
    stated_text: str
    enacted_tool: Optional[str]
    enacted_args: dict[str, Any]
    action_compliant: bool
    stated_vs_enacted_consistent: bool
    provider: str
    model: str
    timestamp: str
    # Kept for readability/provenance; beyond the required spec fields.
    action_reason: str = ""
    consistency_judge: str = "heuristic"
    consistency_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "condition": self.condition,
            "stated_text": self.stated_text,
            "enacted_tool": self.enacted_tool,
            "enacted_args": self.enacted_args,
            "action_compliant": self.action_compliant,
            "stated_vs_enacted_consistent": self.stated_vs_enacted_consistent,
            "action_reason": self.action_reason,
            "consistency_judge": self.consistency_judge,
            "consistency_reason": self.consistency_reason,
            "provider": self.provider,
            "model": self.model,
            "timestamp": self.timestamp,
        }


def conditions() -> list[Condition]:
    """The small-but-real 2x2 condition set.

    Varies rule salience (stated vs omitted) and reasoning visibility
    (chain-of-thought shown vs hidden).
    """
    return [
        Condition("rule_stated__cot_hidden", rule_salient=True, show_cot=False),
        Condition("rule_stated__cot_shown", rule_salient=True, show_cot=True),
        Condition("rule_omitted__cot_hidden", rule_salient=False, show_cot=False),
        Condition("rule_omitted__cot_shown", rule_salient=False, show_cot=True),
    ]
