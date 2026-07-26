"""Tests for LLM provider protocol and data types."""

import pytest
from komikan.agent.provider import (
    LLMProvider,
    ToolCall,
    ToolDefinition,
    ToolResult,
    LLMResponse,
    KOMIKAN_TOOLS,
)


class TestToolCall:
    def test_tool_call_creation(self):
        tc = ToolCall(name="make_move", arguments={"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2})
        assert tc.name == "make_move"
        assert tc.arguments == {"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2}

    def test_tool_call_is_immutable(self):
        tc = ToolCall(name="make_move", arguments={})
        with pytest.raises(AttributeError):
            tc.name = "other"

    def test_tool_call_equality(self):
        tc1 = ToolCall(name="make_move", arguments={"from_x": 1})
        tc2 = ToolCall(name="make_move", arguments={"from_x": 1})
        assert tc1 == tc2

    def test_tool_call_inequality(self):
        tc1 = ToolCall(name="make_move", arguments={"from_x": 1})
        tc2 = ToolCall(name="make_move", arguments={"from_x": 2})
        assert tc1 != tc2


class TestToolDefinition:
    def test_tool_definition_creation(self):
        td = ToolDefinition(
            name="make_move",
            description="Execute a move",
            parameters={"type": "object", "properties": {}},
        )
        assert td.name == "make_move"
        assert td.description == "Execute a move"
        assert td.parameters == {"type": "object", "properties": {}}


class TestToolResult:
    def test_tool_result_success(self):
        tr = ToolResult(success=True, data={"status": "ok"})
        assert tr.success is True
        assert tr.data == {"status": "ok"}
        assert tr.error is None

    def test_tool_result_failure(self):
        tr = ToolResult(success=False, error="Invalid move")
        assert tr.success is False
        assert tr.error == "Invalid move"
        assert tr.data is None


class TestLLMResponse:
    def test_response_with_tool_call(self):
        resp = LLMResponse(
            tool_calls=[ToolCall(name="make_move", arguments={"from_x": 0, "from_y": 0, "to_x": 1, "to_y": 1})],
            text=None,
        )
        assert len(resp.tool_calls) == 1
        assert resp.text is None

    def test_response_with_text(self):
        resp = LLMResponse(tool_calls=[], text="I don't know what to do.")
        assert resp.text == "I don't know what to do."
        assert len(resp.tool_calls) == 0

    def test_response_empty(self):
        resp = LLMResponse(tool_calls=[], text=None)
        assert resp.text is None
        assert len(resp.tool_calls) == 0


class TestKomikanTools:
    def test_has_make_move_tool(self):
        names = [t.name for t in KOMIKAN_TOOLS]
        assert "make_move" in names

    def test_make_move_parameters(self):
        move_tool = next(t for t in KOMIKAN_TOOLS if t.name == "make_move")
        props = move_tool.parameters["properties"]
        assert "from_x" in props
        assert "from_y" in props
        assert "to_x" in props
        assert "to_y" in props
        required = move_tool.parameters.get("required", [])
        assert "from_x" in required
        assert "from_y" in required
        assert "to_x" in required
        assert "to_y" in required

    def test_make_move_types_are_integer(self):
        move_tool = next(t for t in KOMIKAN_TOOLS if t.name == "make_move")
        props = move_tool.parameters["properties"]
        for key in ("from_x", "from_y", "to_x", "to_y"):
            assert props[key]["type"] == "integer"


class TestLLMProviderProtocol:
    def test_protocol_has_chat_method(self):
        assert hasattr(LLMProvider, "chat")

    def test_custom_class_implements_protocol(self):
        class FakeProvider:
            def chat(self, system_prompt: str, user_prompt: str, tools: list[ToolDefinition]) -> LLMResponse:
                return LLMResponse(tool_calls=[], text="ok")

        provider = FakeProvider()
        assert isinstance(provider, LLMProvider)

    def test_class_missing_chat_is_not_protocol(self):
        class BadProvider:
            pass

        provider = BadProvider()
        assert not isinstance(provider, LLMProvider)
