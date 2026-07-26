"""LLM provider abstraction for Komikan AI agent.

Provides a provider-agnostic Protocol and adapters for OpenAI and Anthropic.
LLM providers are optional dependencies — install with `pip install komikan[llm]`.
"""

import os
from typing import Protocol, runtime_checkable


class LLMError(Exception):
    """Raised when an LLM provider fails."""

    def __init__(self, message: str, *, provider: str | None = None):
        super().__init__(message)
        self.provider = provider


@runtime_checkable
class LLMProtocol(Protocol):
    """Protocol that all LLM providers must implement."""

    async def chat(self, prompt: str) -> str: ...


class OpenAIProvider:
    """OpenAI adapter implementing LLMProtocol."""

    def __init__(self, *, model: str = "gpt-4o", api_key: str | None = None):
        try:
            import openai
        except ImportError as e:
            raise ImportError(
                "openai package is required. Install with: pip install komikan[llm]"
            ) from e

        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise LLMError(
                "OPENAI_API_KEY not set. Pass api_key or set the environment variable.",
                provider="openai",
            )
        self._client = openai.AsyncOpenAI(api_key=resolved_key)
        self._model = model

    async def chat(self, prompt: str) -> str:
        """Send a prompt to OpenAI and return the response text."""
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            if not response.choices:
                raise LLMError("LLM returned empty response", provider="openai")
            return response.choices[0].message.content
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(str(e), provider="openai") from e


class AnthropicProvider:
    """Anthropic adapter implementing LLMProtocol."""

    def __init__(
        self, *, model: str = "claude-sonnet-4-20250514", api_key: str | None = None
    ):
        try:
            import anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package is required. Install with: pip install komikan[llm]"
            ) from e

        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise LLMError(
                "ANTHROPIC_API_KEY not set. Pass api_key or set the environment variable.",
                provider="anthropic",
            )
        self._client = anthropic.AsyncAnthropic(api_key=resolved_key)
        self._model = model

    async def chat(self, prompt: str) -> str:
        """Send a prompt to Anthropic and return the response text."""
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(str(e), provider="anthropic") from e


def LLMProvider(provider_name: str, *, model: str | None = None) -> LLMProtocol:
    """Factory function to create an LLM provider by name.

    Args:
        provider_name: One of "openai", "anthropic".
        model: Optional model override.

    Returns:
        An instance implementing LLMProtocol.

    Raises:
        ValueError: If provider_name is not recognized.
    """
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }

    normalized = provider_name.lower()
    cls = providers.get(normalized)
    if cls is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. Available: {', '.join(providers)}"
        )

    kwargs = {}
    if model:
        kwargs["model"] = model
    return cls(**kwargs)
