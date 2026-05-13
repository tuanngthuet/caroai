# ai/algorithms/minimax.py
from core.constants import BOARD_SIZE, EMPTY, AI, PLAYER, SCORE_WIN
from game.rules import check_winner, get_candidate_moves
from ai.evaluation.evaluation import evaluate_board
from ai.utils.node_counter import NodeCounter

counter = NodeCounter()

def minimax(board, depth, is_maximizing, last_move,
            ai_player=AI, human_player=PLAYER):

    counter.increment()

    winner, _ = check_winner(board, last_move)

    if winner == ai_player:
        return SCORE_WIN + depth

    if winner == human_player:
        return -(SCORE_WIN + depth)

    if depth == 0:
        return evaluate_board(
            board,
            last_move,
            ai_player,
            human_player
        )

    moves = get_candidate_moves(board)

    if not moves:
        return 0

    if is_maximizing:

        best = -float('inf')

        for r, c in moves:

            board[r][c] = ai_player

            val = minimax(
                board,
                depth-1,
                False,
                (r,c),
                ai_player,
                human_player
            )

            board[r][c] = EMPTY

            if val >= SCORE_WIN:
                return val

            best = max(best, val)

        return best

    else:

        best = float('inf')

        for r, c in moves:

            board[r][c] = human_player

            val = minimax(
                board,
                depth-1,
                True,
                (r,c),
                ai_player,
                human_player
            )

            board[r][c] = EMPTY

            if val <= -SCORE_WIN:
                return val

            best = min(best, val)

        return best

def get_best_move_minimax(board, depth, ai_player=AI, human_player=PLAYER):
    counter.reset()
    best_val = -float('inf')
    best_move = None
    moves = get_candidate_moves(board)

    for r, c in moves:
        board[r][c] = ai_player
        val = minimax(board, depth-1, False, (r,c), ai_player, human_player)
        board[r][c] = EMPTY
        if val > best_val:
            best_val = val
            best_move = (r, c)

    return best_move, best_val, counter.get()
