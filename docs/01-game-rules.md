# Komikan Game Rules

## Overview and Origin

Komikan is a traditional board game of the Mapuche people from southern Chile and Argentina. It is an asymmetric hunt game in which one player controls a single powerful piece — the **Pangui** (Puma) — and the other controls a group of weaker pieces — the **Pu Trewa** (Dogs). The game reflects the Mapuche relationship with the natural world and has been played for centuries as both entertainment and cultural practice.

Komikan belongs to the family of hunt/fox games, similar to "Fox and Hounds" or "Tiger and Goats," found in many cultures worldwide.

## Board

The game is played on a 5×8 grid of **nodes** (intersections), connected by orthogonal and diagonal lines. Players move along these connections.

### Special Board Features

- **Disabled Nodes**: Positions (0,2) and (4,2) are blocked and cannot be occupied or traversed.
- **Disabled Paths**: Several diagonal paths in the upper portion of the board (rows 0–3) and certain diagonal paths in the lower portion are disabled to shape the strategic topology of the board. The upper triangle area has restricted diagonal movement to create the distinctive Komikan board shape.

```text
  0   1   2   3   4       (x-axis)

  .---.---.---.---.   0   North start: Pangui at (2,0)
  |   |   |   |   |
  .---.---.---.---.   1
  |       |       |
  X   .---.---.   X   2   X = disabled nodes (0,2) and (4,2)
  |  / \  |  / \  |
  .---.---.---.---.   3
  | \ | / | \ | / |
  .---.---.---.---.   4
  | / | \ | / | \ |
  .---.---.---.---.   5   South flanks: (0,5) and (4,5)
  | \ | / | \ | / |
  .---.---.---.---.   6   South row
  | / | \ | / | \ |
  .---.---.---.---.   7   South row

(y-axis)
```

## Players and Pieces

| Player | Name | Pieces | Color |
|--------|------|--------|-------|
| North | **Pangui** (Puma) | 1 token | Red |
| South | **Pu Trewa** (Dogs) | 12 tokens | Blue |

## Starting Positions

- **North (Pangui)**: 1 token at position **(2, 0)** — center of the top row.
- **South (Pu Trewa)**: 12 tokens placed at:
  - Flanking positions: (0, 5) and (4, 5)
  - Full bottom two rows (y=6 and y=7): all 10 positions

## Turn Order

The **North player (Pangui)** moves first. Players alternate turns.

## Movement

On each turn, a player moves **one** of their tokens to an adjacent node along a valid connection (line on the board).

### Valid Directions

Tokens can move in up to **8 directions**:

- **Orthogonal**: Up, Down, Left, Right
- **Diagonal**: Up-Left, Up-Right, Down-Left, Down-Right

### Restrictions

- A token cannot move to an **occupied** node.
- A token cannot move to a **disabled** node.
- A token cannot move along a **disabled path** (certain diagonals are removed for strategic balance).
- A token cannot move outside the board boundaries.

## Capture Mechanics

**Only the North player (Pangui) can capture.**

### How to Capture

The Pangui captures a South token by **jumping over** it:

1. There must be an enemy (South) token on an adjacent node in any of the 8 directions.
2. The node directly beyond the enemy token (in the same direction) must be **empty** and **valid**.
3. Both the path from the Pangui to the enemy and from the enemy to the landing node must be **valid** (not disabled).
4. The captured South token is removed from the board.

A capture move covers a distance of exactly **2 steps** in one direction.

### Capture Constraints

- The Pangui **cannot** capture its own pieces (N/A — it only has one token).
- The Pangui **cannot** jump over an empty space.
- The Pangui **cannot** land on an occupied or disabled node.
- The Pangui **cannot** jump through disabled paths or over disabled nodes.

## Win Conditions

- **North (Pangui) wins**: By capturing enough South tokens that the South can no longer effectively surround the Pangui. North wins when South has 4 or fewer tokens remaining.
- **South (Pu Trewa) wins**: By surrounding and trapping the Pangui so that it has **no valid moves and no valid captures** available.

### Draw/Stalemate

If the South player has no valid moves on their turn, the game may be declared a stalemate. Proper strategy for South involves coordinated movement to corner the Pangui while avoiding unnecessary losses.
