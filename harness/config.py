"""Environment-driven configuration. No secrets live in the repo."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()  # load .env if present; a no-op otherwise
except ImportError:  # python-dotenv is optional at runtime
    pass


DEFAULT_MODEL = "claude-opus-4-8"


@dataclass(frozen=True)
class Config:
    provider: str
    model: str

    @staticmethod
    def from_env(provider_override: str | None = None) -> "Config":
        provider = (provider_override or os.getenv("LLM_PROVIDER", "mock")).strip().lower()
        model = os.getenv("LLM_MODEL", DEFAULT_MODEL).strip()
        return Config(provider=provider, model=model)
