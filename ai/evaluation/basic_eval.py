# ai/evaluation/basic_eval.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, PLAYER, AI
from core.constants import SCORE_WIN, SCORE_3, SCORE_2, SCORE_BLOCK3

DIRECTIONS = [(0,1),(1,0),(1,1),(1,-1)]

def evaluate_board(board, ai_player=AI, human_player=PLAYER):
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in DIRECTIONS:
                score += _score_line(board, r, c, dr, dc, ai_player, human_player)
    return score

def _score_line(board, r, c, dr, dc, ai, human):
    score = 0
    for player, sign in [(ai, 1), (human, -1)]:
        count = 0
        open_ends = 0
        # forward
        nr, nc = r, c
        for _ in range(WIN_LENGTH):
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if board[nr][nc] == player:
                    count += 1
                elif board[nr][nc] == EMPTY:
                    open_ends += 1
                    break
                else:
                    break
            nr += dr; nc += dc
        # check end open
        er, ec = r + dr*count, c + dc*count
        if 0 <= er < BOARD_SIZE and 0 <= ec < BOARD_SIZE and board[er][ec] == EMPTY:
            open_ends += 1

        if count >= WIN_LENGTH:
            s = SCORE_WIN
        elif count == 3:
            s = SCORE_3 if open_ends == 2 else SCORE_BLOCK3
        elif count == 2:
            s = SCORE_2
        else:
            s = 0
        score += sign * s
    return score
