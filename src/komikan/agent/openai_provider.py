"""OpenAI provider adapter for tool-calling LLM interactions."""

from __future__ import annotations

import json
import logging
import time

from komikan.agent.provider import LLMResponse, ToolCall, ToolDefinition

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0


class OpenAIProvider:
    """OpenAI adapter implementing the LLMProvider protocol."""

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self._api_key = api_key
        self._model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self._api_key)
        return self._client

    @staticmethod
    def _convert_tools(tools: list[ToolDefinition]) -> list[dict[str, object]] | None:
        if not tools:
            return None
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[ToolDefinition],
    ) -> LLMResponse:
        client = self._get_client()
        openai_tools = self._convert_tools(tools)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs: dict[str, object] = {
            "model": self._model,
            "messages": messages,
        }
        if openai_tools is not None:
            kwargs["tools"] = openai_tools

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = client.chat.completions.create(**kwargs)
                break
            except Exception as e:
                last_error = e
                if _is_rate_limit(e) and attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "Rate limited, retrying in %.1fs (attempt %d/%d)",
                        delay,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    time.sleep(delay)
                    continue
                raise
        else:
            raise last_error  # type: ignore[misc]

        message = response.choices[0].message

        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                )
                for tc in message.tool_calls
            ]
            return LLMResponse(tool_calls=tool_calls, text=None)

        return LLMResponse(tool_calls=[], text=message.content)


def _is_rate_limit(exc: Exception) -> bool:
    return exc.__class__.__name__ == "RateLimitError" or "429" in str(exc)
