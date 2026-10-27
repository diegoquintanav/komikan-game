"""LLM provider protocol and shared types for tool-calling providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ToolCall:
    """A single tool call returned by the LLM."""

    name: str
    arguments: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolDefinition:
    """Schema for a tool the LLM may invoke."""

    name: str
    description: str
    parameters: dict[str, object]


@dataclass(frozen=True)
class ToolResult:
    """Result of executing a tool call against the game API."""

    success: bool
    data: dict[str, object] | None = None
    error: str | None = None


@dataclass(frozen=True)
class LLMResponse:
    """Unified response from any LLM provider."""

    tool_calls: list[ToolCall] = field(default_factory=list)
    text: str | None = None


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol that all LLM provider adapters must implement."""

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse: ...


KOMIKAN_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="make_move",
        description="Execute a move on the Komikan board. Move one of your tokens from its current position to an adjacent empty node.",
        parameters={
            "type": "object",
            "properties": {
                "from_x": {
                    "type": "integer",
                    "description": "X coordinate of the token to move (0-4)",
                },
                "from_y": {
                    "type": "integer",
                    "description": "Y coordinate of the token to move (0-7)",
                },
                "to_x": {
                    "type": "integer",
                    "description": "X coordinate of the destination (0-4)",
                },
                "to_y": {
                    "type": "integer",
                    "description": "Y coordinate of the destination (0-7)",
                },
            },
            "required": ["from_x", "from_y", "to_x", "to_y"],
        },
    ),
]
