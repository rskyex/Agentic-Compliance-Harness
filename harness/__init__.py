"""Deceptive-compliance evaluation harness.

A miniature of an agentic compliance-evaluation pipeline: per scenario and
condition it asks a model (1) whether it will comply and what it will do, then
(2) gives it the same rule + request with a mock tool and records the actual
tool call. A checker compares stated words against the enacted action.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
