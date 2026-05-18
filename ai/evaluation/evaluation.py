# ai/evaluation/evaluation.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, PLAYER, AI, SCORE_WIN

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

# Pattern scores: keyed by (count, open_ends)
# open_ends: 0 = both blocked, 1 = one open, 2 = both open
_AI_SCORE = {
    (4, 2): SCORE_WIN,        # open-4  → guaranteed win
    (4, 1): 50_000,           # blocked-4 → win next move
    (4, 0): 0,                # dead
    (3, 2): 5_000,            # open-3  → strong threat
    (3, 1): 500,              # blocked-3
    (3, 0): 0,
    (2, 2): 200,
    (2, 1): 50,
    (2, 0): 0,
}
_HU_SCORE = {
    (4, 2): SCORE_WIN,
    (4, 1): 45_000,           # slightly less than AI so AI prefers winning over blocking
    (4, 0): 0,
    (3, 2): 4_000,
    (3, 1): 400,
    (3, 0): 0,
    (2, 2): 150,
    (2, 1): 40,
    (2, 0): 0,
}


def _score_sequence(board, r, c, dr, dc, player, opponent):
    """
    Starting at (r,c) going in direction (dr,dc), count consecutive `player`
    pieces and check openness of both ends.
    Returns score contribution for this sequence.
    """
    count = 0
    nr, nc = r, c
    while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
        count += 1
        nr += dr
        nc += dc

    if count == 0:
        return 0

    # Check forward end (after the run)
    fwd_open = (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY)

    # Check backward end (before start)
    br, bc = r - dr, c - dc
    bwd_open = (0 <= br < BOARD_SIZE and 0 <= bc < BOARD_SIZE and board[br][bc] == EMPTY)

    open_ends = int(fwd_open) + int(bwd_open)

    if count >= WIN_LENGTH:
        return SCORE_WIN

    table = _AI_SCORE if player != opponent else _HU_SCORE
    # We always call with player=ai or player=human, so pick the right table outside
    return table.get((count, open_ends), 0)


def evaluate_board(board, move, ai_player=AI, human_player=PLAYER):
    """
    Full-board evaluation. Scans every cell in every direction,
    only counting each run once (from its leftmost/topmost cell).
    """
    score = 0
    visited = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]  # per-direction tracking done inline

    for dr, dc in DIRECTIONS:
        seen = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if seen[r][c]:
                    continue
                v = board[r][c]
                if v == EMPTY:
                    continue

                # Only start a run from the beginning of a sequence
                pr, pc = r - dr, c - dc
                if 0 <= pr < BOARD_SIZE and 0 <= pc < BOARD_SIZE and board[pr][pc] == v:
                    continue  # not the start of this run

                # Count run length and mark visited
                count = 0
                nr, nc = r, c
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == v:
                    seen[nr][nc] = True
                    count += 1
                    nr += dr
                    nc += dc

                if count >= WIN_LENGTH:
                    if v == ai_player:
                        score += SCORE_WIN
                    else:
                        score -= SCORE_WIN
                    continue

                # Check openness
                fwd_open = (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE
                            and board[nr][nc] == EMPTY)
                br, bc = r - dr, c - dc
                bwd_open = (0 <= br < BOARD_SIZE and 0 <= bc < BOARD_SIZE
                            and board[br][bc] == EMPTY)
                open_ends = int(fwd_open) + int(bwd_open)

                if v == ai_player:
                    score += _AI_SCORE.get((count, open_ends), 0)
                else:
                    score -= _HU_SCORE.get((count, open_ends), 0)

    return score
