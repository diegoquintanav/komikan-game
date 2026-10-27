# 02 - LLM Agent

Komikan ships with an LLM agent that plays either side through the REST API. The agent sees game state as a text prompt, queries a model with tool-calling, and validates every move before executing it.

## Setup

### 1. Install with LLM extras

The agent SDKs are optional:

```bash
uv sync --extra llm
# or
pip install komikan-game[llm]
```

This pulls in `openai` and `anthropic` packages. If you only need one provider, install just that package — the agent will skip unused SDKs.

### 2. Set your API key

```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Start the API server

```bash
uv run python -m uvicorn komikan.api.main:app --port 8000
# runs on http://localhost:8000
```

The agent communicates over HTTP, so it works against any running server — local or remote.

### 4. OpenCode Go (optional)

The agent also supports the OpenCode Go gateway, an OpenAI-compatible endpoint:

```bash
export OPENCODE_GO_API_KEY=oc_sk_...
uv run komikan-agent --provider opencode-go --model deepseek-v4.1-flash \
  --base-url http://localhost:8000
```

The gateway requires an `x-opencode-session` header. The provider generates a stable session id automatically; override it with `--session-id`. Use `--llm-base-url` to point at a custom LLM endpoint. Note that `--base-url` is the Komikan game API, not the LLM endpoint.

## Running the agent

```bash
uv run komikan-agent
```

Defaults to **OpenAI gpt-4o playing as North (Pangui)** against a random opponent.

### Key flags

| Flag | Default | Description |
|---|---|---|
| `--provider` | `openai` | LLM provider: `openai`, `anthropic`, or `opencode-go` |
| `--model` | `gpt-4o` (openai) / `claude-sonnet-4-20250514` (anthropic) / `deepseek-v4.1-flash` (opencode-go) | Model to use |
| `--side` | `north` | Which side to play: `north` (Pangui) or `south` (Pu Trewa) |
| `--opponent` | `random` | Opponent type: `random` (AI) or `human` |
| `--delay` | `0.5` | Seconds between moves (easier to follow) |
| `--base-url` | `http://localhost:8000` | Komikan game API server URL |
| `--llm-base-url` | none | OpenAI-compatible LLM endpoint override |
| `--session-id` | generated | `x-opencode-session` header value for OpenCode Go |

### Examples

**OpenAI vs random:**
```bash
uv run komikan-agent --provider openai --model gpt-4o
```

**Anthropic vs random:**
```bash
uv run komikan-agent --provider anthropic --model claude-sonnet-4-20250514 --side south
```

**Play against the agent (human):**
```bash
uv run komikan-agent --opponent human --delay 0.5
```

The human plays via the API docs UI at `http://localhost:8000/docs` — make moves there, and the agent responds automatically.

**Remote server:**
```bash
uv run komikan-agent --base-url https://your-server.example.com --side south
```

## How it works

1. Agent creates a game via `POST /api/games`
2. On each turn, it fetches game state and legal moves
3. It sends the state to the LLM as a structured prompt
4. LLM responds by calling the `make_move` tool with coordinates
5. Agent validates the move is legal, then executes it
6. On invalid moves, it retries with corrected context (up to 3 attempts)
7. If all retries fail, falls back to a random legal move (game never stalls)

## Architecture

See [ADR-006](adr/006-llm-agent-integration.md) for the full decision record.

```
komikan-agent CLI
    |
    v
KomikanAgent  --- play_turn() ---+
    |                              |
    +-- LLMProvider (OpenAI)       |
    +-- LLMProvider (Anthropic)    |
    |                              |
    +-- HTTP client <------+       |
         |                 |       |
         v                 |       |
    REST API  <------------+       |
         |                         |
    GameBoard                      |
         |                         |
    Opponent (random/human)  <-----+
```
