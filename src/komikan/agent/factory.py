"""Factory function for creating LLM provider instances by name."""

from __future__ import annotations

from komikan.agent.provider import LLMProvider

_PROVIDERS: dict[str, type] = {
    "openai": None,  # lazy import
    "anthropic": None,
}


def create_provider(name: str, **kwargs: object) -> LLMProvider:
    """Create an LLM provider by name.

    Supported names: "openai", "anthropic".
    """
    normalized = name.lower()
    if normalized not in _PROVIDERS:
        supported = ", ".join(sorted(_PROVIDERS.keys()))
        raise ValueError(f"Unknown provider '{name}'. Supported: {supported}")

    if normalized == "openai":
        from komikan.agent.openai_provider import OpenAIProvider

        return OpenAIProvider(**kwargs)  # type: ignore[return-value]
    else:
        from komikan.agent.anthropic_provider import AnthropicProvider

        return AnthropicProvider(**kwargs)  # type: ignore[return-value]
