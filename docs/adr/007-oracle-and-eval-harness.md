# ADR-007: Oracle and Eval Harness Before MCP Integration

## Status

Accepted. The initiative was reordered: Oracle and Eval Harness is Project 2, MCP plus RAG is Project 3, and the Research Track remains Project 4. ALMUD-280 defines this specification; ALMUD-281 to ALMUD-288 are the implementation tickets.

## Context

ADR-004 gave the project a REST API and ADR-006 shipped an LLM agent that plays full legal games through it. The agent's strength, however, is unmeasured: win rate against `RandomOpponent` says little, because a random legal walk also produces legal games. Every near-term decision (the rules system prompt, temperature, provider and model choice, and any MCP demo claim) needs a baseline to compare against.

The initiative originally ordered Project 2 as Agentic Stack Integration (MCP plus RAG) and Project 3 as Baseline Oracle and Eval Harness, on the argument that MCP is the cheaper and more demoable artifact for a general-SWE audience. ADR-005 (MCP server with FastMCP) still records that plan and remains Proposed and unimplemented.

Two facts argue for reversing the order. First, MCP is a distribution layer: it makes the agent reachable, not better. Demoing an unmeasured agent weakens the story. Second, the board is small (5x8, roughly 8 moves for North and 24 for South), so a negamax oracle with alpha-beta at depth 3 or 4 is cheap in pure Python and reuses the existing engine.

## Decision

1. Build a minimal Baseline Oracle and Eval Harness before the MCP plus RAG integration.
2. Scope the project to the eight backlog items: static evaluation, negamax oracle, state mirror, `OracleOpponent`, match runner, structured per-move logging, budget gate, aggregation and reporting, minimal dashboard, and comparative sweep. No leaderboard and no persistent service.
3. Make the oracle and random players deterministic given `(state, depth, seed)`. Record provider, model, temperature, and seed for LLM runs, because LLM sampling cannot be seeded.
4. Report raw counts and Wilson 95 percent intervals. Do not claim significance below N=20.
5. Renumber the roadmap: Oracle and Eval Harness becomes Project 2 and Agentic Stack Integration becomes Project 3. Done in Linear; the project was renamed and ALMUD-280 to ALMUD-288 were created.
6. Leave ADR-005 in Proposed until MCP work actually starts.

## Consequences

Positive:

- The agent gets a reproducible quality signal before more stack is built.
- Prompt, temperature, and provider decisions become comparable instead of anecdotal.
- The research track gains the measurement foundation it needs.

Negative:

- The demoable MCP artifact arrives later.
- The eval adds roughly 700 to 900 lines and an oracle that must be maintained.
- Small-N results will be directional only, which can frustrate early comparisons.

Mitigations:

- Small N defaults, fixed default depth, and per-game cost reporting.
- Larger sweeps and deeper search are opt-in flags.
- Explicitly label low-N results as directional in every report.

## Follow-ups

- Update the Komikan Game initiative description and project names to reflect the reversed order.
- Create the Linear issues for the oracle and eval work before apply.
- Correct the stale `Opponent` protocol description in the komikan-1 design document: the source signature is `choose_move() -> dict[str, int]`.

## References

- ADR-004: REST API and Web Interface
- ADR-005: MCP Server with FastMCP and AI Agents (Proposed)
- ADR-006: LLM Agent Integration
- ALMUD-280 (specification) and ALMUD-281 to ALMUD-288 (implementation tickets)
- Change: `openspec/changes/komikan-2-oracle-eval/`
