# ai/heuristics/move_ordering.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, AI, PLAYER, SCORE_WIN
from game.rules import check_winner


def _quick_score(board, r, c, player, opponent):
    """Fast inline threat score for a single cell placement."""
    DIRS = [(0, 1), (1, 0), (1, 1), (1, -1)]
    score = 0
    for dr, dc in DIRS:
        count = 1
        open_ends = 0
        for sign in (1, -1):
            nr, nc = r + sign * dr, c + sign * dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
                count += 1
                nr += sign * dr
                nc += sign * dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                open_ends += 1
        if count >= WIN_LENGTH:
            return SCORE_WIN
        score += count * count * (open_ends + 1)
    return score


def order_moves(board, moves, ai_player=AI, human_player=PLAYER):
    """
    Sort moves by threat priority:
      1. Immediate AI win
      2. Block immediate human win
      3. Best combined threat score (AI attack + human block value)
    """
    wins, blocks, rest = [], [], []

    for r, c in moves:
        # Check AI immediate win
        board[r][c] = ai_player
        w, _ = check_winner(board, (r, c))
        board[r][c] = EMPTY
        if w == ai_player:
            wins.append((r, c))
            continue

        # Check human immediate win (must block)
        board[r][c] = human_player
        w, _ = check_winner(board, (r, c))
        board[r][c] = EMPTY
        if w == human_player:
            blocks.append((r, c))
            continue

        # Score by combined attack + defense value
        board[r][c] = ai_player
        atk = _quick_score(board, r, c, ai_player, human_player)
        board[r][c] = EMPTY
        board[r][c] = human_player
        dfn = _quick_score(board, r, c, human_player, ai_player)
        board[r][c] = EMPTY
        rest.append((atk + dfn, r, c))

    rest.sort(key=lambda x: -x[0])
    return wins + blocks + [(r, c) for _, r, c in rest]
