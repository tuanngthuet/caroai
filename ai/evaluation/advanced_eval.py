# ai/evaluation/advanced_eval.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, PLAYER, AI
from core.constants import SCORE_WIN, SCORE_4, SCORE_3, SCORE_2, SCORE_BLOCK3, SCORE_BLOCK4

DIRECTIONS = [(0,1),(1,0),(1,1),(1,-1)]

def score_segment(segment, player, opponent):
    if opponent in segment or -1 in segment:
        return 0

    p = segment.count(player)
    e = segment.count(EMPTY)

    if p == 4 :
        return SCORE_WIN

    if p == 3 and e == 1:
        return SCORE_3

    if p == 2 and e == 2:
        return SCORE_2

    return 0

def evaluate_board(board, ai_player=AI, human_player=PLAYER):
    score = 0
    center = BOARD_SIZE // 2
    # Center bonus
    for r in range(center-3, center+4):
        for c in range(center-3, center+4):
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if board[r][c] == ai_player:
                    score += 3
                elif board[r][c] == human_player:
                    score -= 3

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in DIRECTIONS:
                seg = []
                for i in range(WIN_LENGTH):
                    nr, nc = r+i*dr, c+i*dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        seg.append(board[nr][nc])
                    else:
                        seg.append(-1)  # wall
                if len(seg) < WIN_LENGTH:
                    continue
                score += score_segment(seg, ai_player, human_player)
                score -= score_segment(seg, human_player, ai_player)
    return score
