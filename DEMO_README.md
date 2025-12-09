# Komikan Game Endgame Demos

This directory contains demo scripts to showcase the endgame conditions in the Komikan board game.

## Available Demos

### 1. `endgame_demo.py` - North Win Demo
**Quick win demonstration**

Launches a game where North (red) is positioned to win by capturing one South token:
- South has exactly 4 tokens
- North can capture one to reduce South to 3 tokens
- Triggers "North wins! South has only 3 tokens left" condition

**How to play:**
- North token is at (2,4)
- Click North token, then click (0,6) to capture the South token at (1,5)
- Or press `A` key to move left and capture
- Game ends immediately with North victory

### 2. `demo_launcher.py` - Multiple Demo Options
**Interactive demo launcher**

Provides three different endgame scenarios:

1. **North Win Demo** - Same as `endgame_demo.py`
2. **South Win Demo** - Complex scenario where South can block North's moves
3. **Full Endgame Demo** - North has multiple capture options

## Running the Demos

```bash
# Quick North win demo
python endgame_demo.py

# Interactive demo launcher with multiple options
python demo_launcher.py
```

## Controls

- **Mouse**: Click to select piece, click destination to move
- **Keyboard**: WASD/Arrow keys to move, QE/ZC for diagonals
- **Restart**: After game ends, press any key to restart
- **Exit**: Press ESC twice to exit

## Win Conditions Demonstrated

1. **North wins**: When South has ≤3 tokens remaining
2. **South wins**: When North has no valid moves available

These demos let you experience both win conditions and see the endgame UI in action!