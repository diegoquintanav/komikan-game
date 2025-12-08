# Debug Logging System

The Komikan game includes a comprehensive debug logging system that tracks all player movements and capture attempts for replay and analysis.

## Enabling Debug Logging

To enable debug logging, set the `KOMIKAN_DEBUG` environment variable to `1`:

```bash
# Run with debug logging
KOMIKAN_DEBUG=1 uv run python main.py

# Or export the variable
export KOMIKAN_DEBUG=1
uv run python main.py
```

## Log File Output

When debug logging is enabled, the game creates a `komikan_game.log` file with:

- **Game Start Information**: Timestamp and initial player setup
- **Move Attempts**: Every movement attempt with player, positions, and token numbers
- **Move Results**: Success/failure status with detailed reasons
- **Capture Events**: Detailed logging of capture attempts and results
- **Game State**: Current board state after each successful move
- **Structured JSON Events**: Machine-readable event data for replay systems

## Log Analysis

Use the included `test_logging.py` script to analyze log files:

```bash
python test_logging.py
```

This will display:
- Game session information
- Chronological list of all moves and captures
- Replay instructions with step-by-step moves
- Detailed analysis of game events

## Log Format Examples

### Game Start
```
2025-12-08 17:31:09,131 - INFO - === KOMIKAN GAME STARTED ===
2025-12-08 17:31:09,131 - INFO - Game start time: 2025-12-08T17:31:09.131205
2025-12-08 17:31:09,131 - INFO - North player: 1 token at (2, 0)
2025-12-08 17:31:09,131 - INFO - South player: 12 tokens across bottom two rows
```

### Move Attempt
```
2025-12-08 17:31:15,245 - DEBUG - MOVE ATTEMPT: NORTH (token #1) (2, 0) -> (2, 1)
2025-12-08 17:31:15,246 - INFO - ✓ MOVE SUCCESS: NORTH moved to (2, 1)
```

### Capture Attempt
```
2025-12-08 17:31:22,108 - DEBUG - CAPTURE ATTEMPT: NORTH (token #1) (2, 3) -> (2, 5)
2025-12-08 17:31:22,109 - INFO - ✓ CAPTURE SUCCESS: Captured south token #7
```

### Failed Move
```
2025-12-08 17:31:18,567 - DEBUG - MOVE ATTEMPT: SOUTH (token #3) (1, 6) -> (0, 2)
2025-12-08 17:31:18,568 - WARNING - ✗ MOVE FAILED: Invalid move - position blocked or out of bounds
```

### Structured JSON Event
```
2025-12-08 17:31:15,246 - DEBUG - GAME_EVENT: {
    "timestamp": "2025-12-08T17:31:15.246123",
    "game_time_seconds": 6.115,
    "move_number": 1,
    "player": "pangui",
    "from_position": [2, 0],
    "to_position": [2, 1],
    "token_number": 1,
    "is_capture_attempt": false,
    "action_type": "move",
    "success": true,
    "captured_token_number": null,
    "failure_reason": null,
    "result_timestamp": "2025-12-08T17:31:15.246145"
}
```

## Replay System

The logging system captures enough information to perfectly replay any game:

1. **Initial Setup**: Player starting positions and token numbers
2. **Move Sequence**: Chronological order of all moves and captures
3. **Board State**: Position tracking after each successful move
4. **Timing Information**: Game duration and move timing
5. **Validation Data**: Success/failure reasons for debugging

## Use Cases

- **Game Analysis**: Study successful strategies and common mistakes
- **Bug Reproduction**: Replay exact sequences that caused issues
- **Tournament Records**: Official game records for competitive play
- **AI Training**: Generate training data for AI players
- **Development**: Debug game mechanics and validate rules

## Performance Notes

Debug logging adds minimal overhead to the game:
- Logs are written asynchronously
- Only enabled when `KOMIKAN_DEBUG=1` is set
- File I/O is optimized for game performance
- Memory usage remains constant regardless of game length

## File Management

Log files accumulate over time. To manage them:

```bash
# View current log
tail -f komikan_game.log

# Archive old logs
mv komikan_game.log komikan_game_$(date +%Y%m%d_%H%M%S).log

# Clean up old logs
find . -name "komikan_game_*.log" -mtime +30 -delete
```