"""Tests for the LLM provider abstraction."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestLLMProtocol:
    """Test that LLMProtocol defines the expected interface."""

    def test_protocol_has_chat_method(self):
        """LLMProtocol must define a chat method."""
        from komikan.llm import LLMProtocol

        assert hasattr(LLMProtocol, "chat")

    def test_protocol_is_protocol(self):
        """LLMProtocol must be a typing.Protocol."""
        from typing import Protocol
        from komikan.llm import LLMProtocol

        assert issubclass(LLMProtocol, Protocol)


class TestLLMError:
    """Test the LLMError exception class."""

    def test_llm_error_is_exception(self):
        """LLMError must be an Exception subclass."""
        from komikan.llm import LLMError

        assert issubclass(LLMError, Exception)

    def test_llm_error_carry_message(self):
        """LLMError must carry a message string."""
        from komikan.llm import LLMError

        err = LLMError("something failed")
        assert str(err) == "something failed"

    def test_llm_error_carry_provider_name(self):
        """LLMError must carry the provider name."""
        from komikan.llm import LLMError

        err = LLMError("fail", provider="openai")
        assert err.provider == "openai"

    def test_llm_error_default_provider(self):
        """LLMError provider defaults to None."""
        from komikan.llm import LLMError

        err = LLMError("fail")
        assert err.provider is None


class TestOpenAIProvider:
    """Test the OpenAI adapter."""

    @pytest.mark.asyncio
    async def test_openai_provider_chat(self):
        """OpenAIProvider.chat() must return a string from the LLM."""
        from komikan.llm import OpenAIProvider

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello from OpenAI"))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider._client = mock_client
        provider._model = "gpt-4o"

        result = await provider.chat("What is Komikan?")
        assert result == "Hello from OpenAI"

    @pytest.mark.asyncio
    async def test_openai_provider_raises_on_failure(self):
        """OpenAIProvider must raise LLMError on API failure."""
        from komikan.llm import OpenAIProvider, LLMError

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("rate limited")
        )

        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider._client = mock_client
        provider._model = "gpt-4o"

        with pytest.raises(LLMError, match="rate limited"):
            await provider.chat("test")

    @pytest.mark.asyncio
    async def test_openai_provider_empty_response(self):
        """OpenAIProvider must raise LLMError on empty response."""
        from komikan.llm import OpenAIProvider, LLMError

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider._client = mock_client
        provider._model = "gpt-4o"

        with pytest.raises(LLMError, match="empty"):
            await provider.chat("test")


class TestAnthropicProvider:
    """Test the Anthropic adapter."""

    @pytest.mark.asyncio
    async def test_anthropic_provider_chat(self):
        """AnthropicProvider.chat() must return a string from the LLM."""
        from komikan.llm import AnthropicProvider

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello from Claude")]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider._client = mock_client
        provider._model = "claude-sonnet-4-20250514"

        result = await provider.chat("What is Komikan?")
        assert result == "Hello from Claude"

    @pytest.mark.asyncio
    async def test_anthropic_provider_raises_on_failure(self):
        """AnthropicProvider must raise LLMError on API failure."""
        from komikan.llm import AnthropicProvider, LLMError

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=Exception("overloaded")
        )

        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider._client = mock_client
        provider._model = "claude-sonnet-4-20250514"

        with pytest.raises(LLMError, match="overloaded"):
            await provider.chat("test")


class TestLLMProviderFactory:
    """Test the LLMProvider factory function."""

    def test_factory_returns_openai(self):
        """LLMProvider('openai') must return an OpenAIProvider instance."""
        from komikan.llm import LLMProvider, OpenAIProvider

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = LLMProvider("openai")
            assert isinstance(provider, OpenAIProvider)

    def test_factory_returns_anthropic(self):
        """LLMProvider('anthropic') must return an AnthropicProvider instance."""
        from komikan.llm import LLMProvider, AnthropicProvider

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = LLMProvider("anthropic")
            assert isinstance(provider, AnthropicProvider)

    def test_factory_unknown_provider(self):
        """LLMProvider must raise ValueError for unknown providers."""
        from komikan.llm import LLMProvider

        with pytest.raises(ValueError, match="Unknown provider"):
            LLMProvider("ollama")

    def test_factory_case_insensitive(self):
        """LLMProvider must be case-insensitive."""
        from komikan.llm import LLMProvider, OpenAIProvider

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = LLMProvider("OpenAI")
            assert isinstance(provider, OpenAIProvider)

    def test_factory_custom_model(self):
        """LLMProvider must accept a model parameter."""
        from komikan.llm import LLMProvider, OpenAIProvider

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = LLMProvider("openai", model="gpt-4o-mini")
            assert isinstance(provider, OpenAIProvider)
            assert provider._model == "gpt-4o-mini"
