"""Tests for OpenAI provider implementation."""

import pytest
from unittest.mock import MagicMock
from komikan.agent.provider import LLMProvider, ToolDefinition, LLMResponse


class TestOpenAIProvider:
    def test_import(self):
        from komikan.agent.openai_provider import OpenAIProvider
        assert OpenAIProvider is not None

    def test_implements_protocol(self):
        from komikan.agent.openai_provider import OpenAIProvider
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        assert isinstance(provider, LLMProvider)

    def test_chat_returns_llm_response(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "Move piece from (0,1) to (1,2)"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client

        resp = provider.chat(
            system_prompt="You are a Komikan player.",
            user_prompt="Current board state...",
            tools=[],
        )
        assert isinstance(resp, LLMResponse)
        assert resp.text == "Move piece from (0,1) to (1,2)"
        assert len(resp.tool_calls) == 0

    def test_chat_parses_tool_calls(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "make_move"
        mock_tool_call.function.arguments = '{"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2}'
        mock_message.tool_calls = [mock_tool_call]
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client

        resp = provider.chat(
            system_prompt="You are a Komikan player.",
            user_prompt="Current board state...",
            tools=[ToolDefinition(name="make_move", description="Move", parameters={"type": "object", "properties": {}})],
        )
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].name == "make_move"
        assert resp.tool_calls[0].arguments == {"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2}

    def test_chat_converts_tool_definitions_to_openai_format(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "ok"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client

        tools = [
            ToolDefinition(
                name="make_move",
                description="Execute a move",
                parameters={"type": "object", "properties": {"from_x": {"type": "integer"}}},
            )
        ]
        provider.chat(system_prompt="sys", user_prompt="usr", tools=tools)

        call_kwargs = mock_client.chat.completions.create.call_args
        openai_tools = call_kwargs.kwargs.get("tools") or call_kwargs[1].get("tools", [])
        assert len(openai_tools) == 1
        assert openai_tools[0]["type"] == "function"
        assert openai_tools[0]["function"]["name"] == "make_move"

    def test_chat_passes_model(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "ok"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o-mini")
        provider._client = mock_client

        provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs.get("model") == "gpt-4o-mini"

    def test_chat_passes_messages(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "ok"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client

        provider.chat(system_prompt="You are a player", user_prompt="Board state: ...", tools=[])
        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages", [])
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a player"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Board state: ..."

    def test_chat_empty_tool_calls_list(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = []
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client

        resp = provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        assert resp.tool_calls == []
        assert resp.text is None

    def test_chat_no_tools_sends_no_tools_param(self):
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "ok"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client

        provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs.get("tools") is None


class TestOpenAIProviderRateLimit:
    def test_retries_on_rate_limit(self):
        import openai
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()

        rate_limit_error = openai.RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )

        mock_success_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "done"
        mock_choice.message = mock_message
        mock_success_response.choices = [mock_choice]

        mock_client.chat.completions.create.side_effect = [rate_limit_error, rate_limit_error, mock_success_response]

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client
        resp = provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        assert resp.text == "done"
        assert mock_client.chat.completions.create.call_count == 3

    def test_raises_after_max_retries(self):
        import openai
        from komikan.agent.openai_provider import OpenAIProvider

        mock_client = MagicMock()

        rate_limit_error = openai.RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )
        mock_client.chat.completions.create.side_effect = rate_limit_error

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        provider._client = mock_client
        with pytest.raises(openai.RateLimitError):
            provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        assert mock_client.chat.completions.create.call_count == 3
