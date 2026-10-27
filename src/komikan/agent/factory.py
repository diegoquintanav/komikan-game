"""Factory function for creating LLM provider instances by name."""

from __future__ import annotations

import uuid

from komikan.agent.provider import LLMProvider

OPENCODE_GO_BASE_URL = "https://opencode.ai/zen/go/v1"

_PROVIDERS: dict[str, type] = {
    "openai": None,  # lazy import
    "anthropic": None,
    "opencode-go": None,
}


def create_provider(name: str, **kwargs: object) -> LLMProvider:
    """Create an LLM provider by name.

    Supported names: "openai", "anthropic", "opencode-go".
    """
    normalized = name.lower()
    if normalized not in _PROVIDERS:
        supported = ", ".join(sorted(_PROVIDERS.keys()))
        raise ValueError(f"Unknown provider '{name}'. Supported: {supported}")

    if normalized == "openai":
        from komikan.agent.openai_provider import OpenAIProvider

        return OpenAIProvider(**kwargs)  # type: ignore[return-value]
    elif normalized == "opencode-go":
        from komikan.agent.openai_provider import OpenAIProvider

        base_url = kwargs.pop("base_url", OPENCODE_GO_BASE_URL)
        session_id = kwargs.pop("session_id", f"komikan-{uuid.uuid4().hex}")
        return OpenAIProvider(  # type: ignore[return-value]
            base_url=base_url, session_id=session_id, **kwargs
        )
    else:
        from komikan.agent.anthropic_provider import AnthropicProvider

        return AnthropicProvider(**kwargs)  # type: ignore[return-value]
