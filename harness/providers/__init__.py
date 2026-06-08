"""Provider factory: swap the LLM backend via env without touching logic."""

from __future__ import annotations

from ..config import Config
from .base import LLMProvider


def get_provider(config: Config) -> LLMProvider:
    """Return a provider instance for the configured backend.

    SDKs are imported lazily so that, e.g., running in `mock` mode needs
    neither the anthropic nor the openai package installed.
    """
    if config.provider == "mock":
        from .mock_provider import MockProvider

        return MockProvider(model=config.model)
    if config.provider == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(model=config.model)
    if config.provider == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(model=config.model)
    raise ValueError(
        f"Unknown LLM_PROVIDER={config.provider!r}. "
        "Expected one of: mock, anthropic, openai."
    )


__all__ = ["get_provider", "LLMProvider"]
