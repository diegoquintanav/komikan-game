# LLM Provider Abstraction Specification

## Purpose

Provider-agnostic interface so any LLM backend (OpenAI, Anthropic, local) can power the Komikan agent through a uniform protocol.

## Requirements

### Requirement: LLMProvider Protocol

The system SHALL define a `LLMProvider` protocol with a `chat()` method accepting messages and tool definitions, returning a response with tool calls or text.

#### Scenario: Successful tool call response

- GIVEN an LLMProvider instance configured with valid credentials
- WHEN chat() is called with messages and tool definitions
- THEN the response contains either tool_calls (list of {name, arguments}) or text content

#### Scenario: Provider rejects invalid credentials

- GIVEN an LLMProvider with malformed API key
- WHEN chat() is called
- THEN the provider raises an appropriate error (not an unhandled exception)

### Requirement: OpenAI Provider Implementation

The system SHALL provide an OpenAI adapter implementing LLMProvider, wrapping the OpenAI Python SDK's tool-calling API.

#### Scenario: OpenAI tool call round-trip

- GIVEN an OpenAIProvider with valid API key and model (e.g., gpt-4o)
- WHEN chat() is called with Komikan move tool definitions
- THEN the response tool_calls match the OpenAI function-calling response format

#### Scenario: OpenAI provider handles rate limits

- GIVEN an OpenAIProvider receiving a 429 rate-limit response
- WHEN chat() is called
- THEN the provider retries with exponential backoff (up to 3 retries)

### Requirement: Anthropic Provider Implementation

The system SHALL provide an Anthropic adapter implementing LLMProvider, wrapping the Anthropic Python SDK's tool-use API.

#### Scenario: Anthropic tool use round-trip

- GIVEN an AnthropicProvider with valid API key and model (e.g., claude-sonnet-4-20250514)
- WHEN chat() is called with Komikan move tool definitions
- THEN the response tool_calls match the Anthropic tool_use response format

#### Scenario: Anthropic provider handles rate limits

- GIVEN an AnthropicProvider receiving a 429 rate-limit response
- WHEN chat() is called
- THEN the provider retries with exponential backoff (up to 3 retries)

### Requirement: Provider Factory

The system SHALL provide a factory function `create_provider(name, **kwargs)` returning an LLMProvider instance by name ("openai" or "anthropic").

#### Scenario: Factory creates OpenAI provider

- GIVEN the string "openai" and api_key kwarg
- WHEN create_provider("openai", api_key="sk-...") is called
- THEN the returned instance implements LLMProvider and delegates to OpenAI

#### Scenario: Factory rejects unknown provider

- GIVEN the string "ollama"
- WHEN create_provider("ollama") is called
- THEN a ValueError is raised with message listing supported providers
