"""Tests for provider factory."""

import pytest
from komikan.agent.provider import LLMProvider


class TestProviderFactory:
    def test_import(self):
        from komikan.agent.factory import create_provider

        assert callable(create_provider)

    def test_creates_openai_provider(self):
        from komikan.agent.factory import create_provider
        from komikan.agent.openai_provider import OpenAIProvider

        provider = create_provider("openai", api_key="sk-test", model="gpt-4o")
        assert isinstance(provider, OpenAIProvider)
        assert isinstance(provider, LLMProvider)

    def test_creates_anthropic_provider(self):
        from komikan.agent.factory import create_provider
        from komikan.agent.anthropic_provider import AnthropicProvider

        provider = create_provider(
            "anthropic", api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        assert isinstance(provider, AnthropicProvider)
        assert isinstance(provider, LLMProvider)

    def test_rejects_unknown_provider(self):
        from komikan.agent.factory import create_provider

        with pytest.raises(ValueError, match="ollama"):
            create_provider("ollama")

    def test_rejects_empty_string(self):
        from komikan.agent.factory import create_provider

        with pytest.raises(ValueError):
            create_provider("")

    def test_case_insensitive(self):
        from komikan.agent.factory import create_provider
        from komikan.agent.openai_provider import OpenAIProvider

        provider = create_provider("OpenAI", api_key="sk-test", model="gpt-4o")
        assert isinstance(provider, OpenAIProvider)

    def test_passes_kwargs_to_provider(self):
        from komikan.agent.factory import create_provider
        from komikan.agent.openai_provider import OpenAIProvider

        provider = create_provider("openai", api_key="sk-custom", model="gpt-4o-mini")
        assert isinstance(provider, OpenAIProvider)
