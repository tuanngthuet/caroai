# ai/algorithms/alphabeta.py
from core.constants import AI, PLAYER, SCORE_WIN, EMPTY
from game.rules import check_winner, get_candidate_moves
from ai.evaluation.basic_eval import evaluate_board
from ai.utils.node_counter import NodeCounter

counter = NodeCounter()

def alphabeta(board, depth, alpha, beta, is_maximizing, last_move, ai_player=AI, human_player=PLAYER):
    counter.increment()

    winner, _ = check_winner(board, last_move)
    if winner == ai_player:
        return SCORE_WIN - depth
    if winner == human_player:
        return -(SCORE_WIN - depth)
    if depth == 0:
        return evaluate_board(board, ai_player, human_player)

    moves = get_candidate_moves(board)
    if not moves:
        return 0

    if is_maximizing:
        best = -float('inf')
        for r, c in moves:
            board[r][c] = ai_player
            val = alphabeta(board, depth-1, alpha, beta, False, (r,c), ai_player, human_player)
            board[r][c] = EMPTY
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float('inf')
        for r, c in moves:
            board[r][c] = human_player
            val = alphabeta(board, depth-1, alpha, beta, True, (r,c), ai_player, human_player)
            board[r][c] = EMPTY
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def get_best_move_alphabeta(board, depth, ai_player=AI, human_player=PLAYER):
    counter.reset()
    best_val = -float('inf')
    best_move = None
    alpha = -float('inf')
    beta = float('inf')
    moves = get_candidate_moves(board)

    for r, c in moves:
        board[r][c] = ai_player
        val = alphabeta(board, depth-1, alpha, beta, False, (r,c), ai_player, human_player)
        board[r][c] = EMPTY
        if val > best_val:
            best_val = val
            best_move = (r, c)
        alpha = max(alpha, best_val)

    return best_move, best_val, counter.get()
