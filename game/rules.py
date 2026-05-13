# game/rules.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, PLAYER, AI

DIRECTIONS = [(0,1),(1,0),(1,1),(1,-1)]

def check_winner(board, last_move):
    if last_move is None:
        return None, []
    r, c = last_move
    player = board[r][c]
    if player == EMPTY:
        return None, []

    for dr, dc in DIRECTIONS:
        cells = [(r, c)]
        for sign in (1, -1):
            nr, nc = r + sign*dr, c + sign*dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
                cells.append((nr, nc))
                nr += sign*dr
                nc += sign*dc
        if len(cells) >= WIN_LENGTH:
            return player, cells
    return None, []

def is_valid(board, r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == EMPTY

def get_candidate_moves(board, radius=2):
    """Only return cells near existing pieces."""
    occupied = {(r,c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] != EMPTY}
    if not occupied:
        center = BOARD_SIZE // 2
        return [(center, center)]
    candidates = set()
    for (or_, oc) in occupied:
        for dr in range(-radius, radius+1):
            for dc in range(-radius, radius+1):
                nr, nc = or_+dr, oc+dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                    candidates.add((nr, nc))
    return list(candidates)
