# ADR-001: Debug Logging System

## Status

Accepted

## Context

The Komikan game needs a comprehensive logging system to track player movements and capture attempts for replay and analysis. This supports game analysis, bug reproduction, tournament records, and AI training data generation.

## Decision

Enable debug logging via the `KOMIKAN_DEBUG` environment variable:

```bash
KOMIKAN_DEBUG=1 uv run python -m komikan
```

When enabled, the system writes to `komikan_game.log` with:

- **Game Start Information**: Timestamp and initial player setup
- **Move Attempts**: Every movement attempt with player, positions, and token numbers
- **Move Results**: Success/failure status with detailed reasons
- **Capture Events**: Detailed logging of capture attempts and results
- **Game State**: Current board state after each successful move
- **Structured JSON Events**: Machine-readable event data for replay systems

### Log Analysis

Use `test_logging.py` to analyze log files:

```bash
python test_logging.py
```

This displays game session information, chronological moves/captures, and replay instructions.

### Performance

- Logs are written asynchronously
- Only enabled when `KOMIKAN_DEBUG=1` is set
- File I/O is optimized for game performance
- Memory usage remains constant regardless of game length

### File Management

```bash
tail -f komikan_game.log                    # View current log
mv komikan_game.log komikan_game_$(date +%Y%m%d_%H%M%S).log  # Archive
find . -name "komikan_game_*.log" -mtime +30 -delete          # Clean up
```

## Consequences

- Developers get full game replay capability from log files
- No performance impact when disabled (default state)
- JSON event format enables automated analysis tooling
- Log files accumulate and need periodic cleanup
