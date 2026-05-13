# ai/evaluation/evaluation.py
from core.constants import BOARD_SIZE, WIN_LENGTH, EMPTY, PLAYER, AI
from core.constants import SCORE_WIN, SCORE_3, SCORE_2, SCORE_BLOCK3

DIRECTIONS = [(0,1),(1,0),(1,1),(1,-1)]

def evaluate_board(board, move, ai_player=AI, human_player=PLAYER):

    if move is None:
        return 0

    r, c = move
    score = 0

    for dr, dc in DIRECTIONS:

        cells = []

        # lấy đoạn dài 9 ô quanh move
        for offset in range(-(WIN_LENGTH-1), WIN_LENGTH):

            nr = r + offset * dr
            nc = c + offset * dc

            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                cells.append(board[nr][nc])
            else:
                cells.append(-1)

        # sliding window size = WIN_LENGTH
        for i in range(len(cells) - WIN_LENGTH + 1):

            segment = cells[i:i+WIN_LENGTH]

            ai_count = 0
            human_count = 0
            empty_count = 0

            for v in segment:

                if v == ai_player:
                    ai_count += 1

                elif v == human_player:
                    human_count += 1

                elif v == EMPTY:
                    empty_count += 1

            # AI patterns
            if human_count == 0:

                if ai_count >= WIN_LENGTH:
                    score += SCORE_WIN

                elif ai_count == 4 and empty_count == 1:
                    score += SCORE_3 * 5

                elif ai_count == 3 and empty_count == 2:
                    score += SCORE_3

                elif ai_count == 2 and empty_count == 3:
                    score += SCORE_2

            # Human patterns
            elif ai_count == 0:

                if human_count >= WIN_LENGTH:
                    score -= SCORE_WIN

                elif human_count == 4 and empty_count == 1:
                    score -= SCORE_3 * 5

                elif human_count == 3 and empty_count == 2:
                    score -= SCORE_3

                elif human_count == 2 and empty_count == 3:
                    score -= SCORE_2

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
