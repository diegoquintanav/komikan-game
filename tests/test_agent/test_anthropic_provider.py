"""Tests for Anthropic provider implementation."""

import pytest
from unittest.mock import MagicMock
from komikan.agent.provider import LLMProvider, ToolDefinition, LLMResponse


class TestAnthropicProvider:
    def test_import(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        assert AnthropicProvider is not None

    def test_implements_protocol(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        assert isinstance(provider, LLMProvider)

    def test_chat_returns_llm_response_text(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.type = "text"
        mock_content_block.text = "I will move my piece forward."
        mock_response.content = [mock_content_block]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        resp = provider.chat(
            system_prompt="You are a Komikan player.",
            user_prompt="Current board state...",
            tools=[],
        )
        assert isinstance(resp, LLMResponse)
        assert resp.text == "I will move my piece forward."
        assert len(resp.tool_calls) == 0

    def test_chat_parses_tool_use_blocks(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_tool_block = MagicMock()
        mock_tool_block.type = "tool_use"
        mock_tool_block.name = "make_move"
        mock_tool_block.input = {"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2}

        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = ""

        mock_response.content = [mock_text_block, mock_tool_block]
        mock_response.stop_reason = "tool_use"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        resp = provider.chat(
            system_prompt="sys",
            user_prompt="usr",
            tools=[
                ToolDefinition(
                    name="make_move",
                    description="Move",
                    parameters={"type": "object", "properties": {}},
                )
            ],
        )
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].name == "make_move"
        assert resp.tool_calls[0].arguments == {
            "from_x": 0,
            "from_y": 1,
            "to_x": 0,
            "to_y": 2,
        }

    def test_chat_multiple_tool_calls(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()

        mock_tool_block1 = MagicMock()
        mock_tool_block1.type = "tool_use"
        mock_tool_block1.name = "make_move"
        mock_tool_block1.input = {"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2}

        mock_tool_block2 = MagicMock()
        mock_tool_block2.type = "tool_use"
        mock_tool_block2.name = "make_move"
        mock_tool_block2.input = {"from_x": 1, "from_y": 1, "to_x": 1, "to_y": 2}

        mock_response.content = [mock_tool_block1, mock_tool_block2]
        mock_response.stop_reason = "tool_use"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        resp = provider.chat(
            system_prompt="sys",
            user_prompt="usr",
            tools=[
                ToolDefinition(
                    name="make_move",
                    description="Move",
                    parameters={"type": "object", "properties": {}},
                )
            ],
        )
        assert len(resp.tool_calls) == 2

    def test_chat_converts_tool_definitions_to_anthropic_format(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        tools = [
            ToolDefinition(
                name="make_move",
                description="Execute a move on the board",
                parameters={
                    "type": "object",
                    "properties": {"from_x": {"type": "integer"}},
                    "required": ["from_x"],
                },
            )
        ]
        provider.chat(system_prompt="sys", user_prompt="usr", tools=tools)

        call_kwargs = mock_client.messages.create.call_args
        anthropic_tools = call_kwargs.kwargs.get("tools") or call_kwargs[1].get(
            "tools", []
        )
        assert len(anthropic_tools) == 1
        assert anthropic_tools[0]["name"] == "make_move"
        assert anthropic_tools[0]["description"] == "Execute a move on the board"
        assert anthropic_tools[0]["input_schema"]["type"] == "object"

    def test_chat_passes_model(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-3-haiku-20240307"
        )
        provider._client = mock_client

        provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("model") == "claude-3-haiku-20240307"

    def test_chat_sends_system_and_user_messages(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        provider.chat(
            system_prompt="You are a player", user_prompt="Board: ...", tools=[]
        )
        call_kwargs = mock_client.messages.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get(
            "messages", []
        )
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Board: ..."
        system = call_kwargs.kwargs.get("system") or call_kwargs[1].get("system", None)
        assert system == "You are a player"

    def test_chat_no_tools_omits_tools_param(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs.get("tools") is None

    def test_chat_no_tool_content_blocks(self):
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_text = MagicMock()
        mock_text.type = "text"
        mock_text.text = "I choose not to move."
        mock_response.content = [mock_text]
        mock_response.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_response

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client

        resp = provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        assert resp.text == "I choose not to move."
        assert resp.tool_calls == []


class TestAnthropicProviderRateLimit:
    def test_retries_on_rate_limit(self):
        import anthropic
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()

        rate_limit_error = anthropic.RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )

        mock_success_response = MagicMock()
        mock_text = MagicMock()
        mock_text.type = "text"
        mock_text.text = "done"
        mock_success_response.content = [mock_text]
        mock_success_response.stop_reason = "end_turn"

        mock_client.messages.create.side_effect = [
            rate_limit_error,
            rate_limit_error,
            mock_success_response,
        ]

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client
        resp = provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        assert resp.text == "done"
        assert mock_client.messages.create.call_count == 3

    def test_raises_after_max_retries(self):
        import anthropic
        from komikan.agent.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()

        rate_limit_error = anthropic.RateLimitError(
            message="rate limited",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )
        mock_client.messages.create.side_effect = rate_limit_error

        provider = AnthropicProvider(
            api_key="sk-ant-test", model="claude-sonnet-4-20250514"
        )
        provider._client = mock_client
        with pytest.raises(anthropic.RateLimitError):
            provider.chat(system_prompt="sys", user_prompt="usr", tools=[])
        assert mock_client.messages.create.call_count == 3
