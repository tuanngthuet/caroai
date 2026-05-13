# ai/heuristics/move_ordering.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, AI, PLAYER
from game.rules import check_winner, get_candidate_moves

def order_moves(board, moves, ai_player=AI, human_player=PLAYER):
    """Sort moves: winning > blocking > center > rest."""
    center = BOARD_SIZE // 2

    def move_priority(move):
        r, c = move
        # Check if AI wins
        board[r][c] = ai_player
        winner, _ = check_winner(board, (r, c))
        board[r][c] = EMPTY
        if winner == ai_player:
            return 0

        # Check if blocking human win
        board[r][c] = human_player
        winner, _ = check_winner(board, (r, c))
        board[r][c] = EMPTY
        if winner == human_player:
            return 1

        # Center proximity
        dist = abs(r - center) + abs(c - center)
        return 2 + dist

    return sorted(moves, key=move_priority)


def filter_candidate_moves(board, radius=2):
    """Only generate moves near existing pieces."""
    return get_candidate_moves(board, radius)
