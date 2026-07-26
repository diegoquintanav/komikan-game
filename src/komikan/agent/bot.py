"""Bot implementations for Komikan AI agent."""

import random
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Move:
    """Represents a move chosen by a bot or parsed from LLM output."""

    from_position: tuple[int, int]
    to_position: tuple[int, int]
    is_capture: bool = False
    captured_position: tuple[int, int] | None = None


@runtime_checkable
class BotProtocol(Protocol):
    """Protocol for bot implementations."""

    def choose_move(self, game) -> Move: ...


class RandomBot:
    """Bot that picks a random valid move."""

    def choose_move(self, game) -> Move:
        """Choose a random valid move from available options.

        Args:
            game: GameInstance with current game state.

        Returns:
            A randomly selected Move.

        Raises:
            ValueError: If no valid moves are available.
        """
        current_player = game.core_state.current_player
        all_advances = []
        all_captures = []

        for pos in current_player.positions:
            from_x, from_y = pos
            valid_moves, valid_captures = game.get_valid_moves(from_x, from_y)

            for move in valid_moves:
                all_advances.append(
                    Move(
                        from_position=(from_x, from_y),
                        to_position=(move.x, move.y),
                        is_capture=False,
                    )
                )

            for to_pos, cap_pos in valid_captures:
                all_captures.append(
                    Move(
                        from_position=(from_x, from_y),
                        to_position=(to_pos.x, to_pos.y),
                        is_capture=True,
                        captured_position=(cap_pos.x, cap_pos.y),
                    )
                )

        all_moves = all_advances + all_captures
        if not all_moves:
            raise ValueError("No valid moves available")

        return random.choice(all_moves)
