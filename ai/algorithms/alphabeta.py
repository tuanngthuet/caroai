# ai/algorithms/alphabeta.py
from core.constants import AI, PLAYER, SCORE_WIN, EMPTY
from game.rules import check_winner, get_candidate_moves
from ai.evaluation.evaluation import evaluate_board
from ai.heuristics.move_ordering import order_moves


def _alphabeta(board, depth, alpha, beta, is_maximizing, last_move,
               ai_player, human_player, counter):
    counter[0] += 1

    winner, _ = check_winner(board, last_move)
    if winner == ai_player:
        return SCORE_WIN + depth      # faster win = higher score
    if winner == human_player:
        return -(SCORE_WIN + depth)   # faster loss = lower score

    if depth == 0:
        return evaluate_board(board, last_move, ai_player, human_player)

    moves = order_moves(board, get_candidate_moves(board), ai_player, human_player)
    if not moves:
        return 0

    if is_maximizing:
        best = -float('inf')
        for r, c in moves:
            board[r][c] = ai_player
            val = _alphabeta(board, depth - 1, alpha, beta, False, (r, c),
                             ai_player, human_player, counter)
            board[r][c] = EMPTY
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break   # β-cutoff
        return best
    else:
        best = float('inf')
        for r, c in moves:
            board[r][c] = human_player
            val = _alphabeta(board, depth - 1, alpha, beta, True, (r, c),
                             ai_player, human_player, counter)
            board[r][c] = EMPTY
            if val < best:
                best = val
            if best < beta:
                beta = best
            if alpha >= beta:
                break   # α-cutoff
        return best


def get_best_move_alphabeta(board, depth, ai_player=AI, human_player=PLAYER):
    """
    Iterative deepening alpha-beta: search depth 1..depth, using the
    previous iteration's best move first for better pruning.
    """
    counter = [0]
    best_move = None
    best_val = -float('inf')

    for d in range(1, depth + 1):
        iter_best_val = -float('inf')
        iter_best_move = None
        alpha = -float('inf')
        beta = float('inf')

        # Put previous best move first for better pruning
        moves = order_moves(board, get_candidate_moves(board), ai_player, human_player)
        if best_move and best_move in moves:
            moves.remove(best_move)
            moves.insert(0, best_move)

        for r, c in moves:
            board[r][c] = ai_player
            val = _alphabeta(board, d - 1, alpha, beta, False, (r, c),
                             ai_player, human_player, counter)
            board[r][c] = EMPTY

            if val > iter_best_val:
                iter_best_val = val
                iter_best_move = (r, c)
            alpha = max(alpha, iter_best_val)

            if iter_best_val >= SCORE_WIN:
                return iter_best_move, iter_best_val, counter[0]

        best_move = iter_best_move
        best_val = iter_best_val

    return best_move, best_val, counter[0]
