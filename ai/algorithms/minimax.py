# ai/algorithms/minimax.py
from core.constants import EMPTY, AI, PLAYER, SCORE_WIN
from game.rules import check_winner, get_candidate_moves
from ai.evaluation.evaluation import evaluate_board
from ai.heuristics.move_ordering import order_moves


def _minimax(board, depth, is_maximizing, last_move, ai_player, human_player, counter):
    counter[0] += 1

    winner, _ = check_winner(board, last_move)
    if winner == ai_player:
        return SCORE_WIN + depth      # prefer faster wins
    if winner == human_player:
        return -(SCORE_WIN + depth)   # prefer slower losses

    if depth == 0:
        return evaluate_board(board, last_move, ai_player, human_player)

    moves = order_moves(board, get_candidate_moves(board), ai_player, human_player)
    if not moves:
        return 0

    if is_maximizing:
        best = -float('inf')
        for r, c in moves:
            board[r][c] = ai_player
            val = _minimax(board, depth - 1, False, (r, c), ai_player, human_player, counter)
            board[r][c] = EMPTY
            if val > best:
                best = val
            if best >= SCORE_WIN:   # can't do better
                break
        return best
    else:
        best = float('inf')
        for r, c in moves:
            board[r][c] = human_player
            val = _minimax(board, depth - 1, True, (r, c), ai_player, human_player, counter)
            board[r][c] = EMPTY
            if val < best:
                best = val
            if best <= -SCORE_WIN:  # can't do worse
                break
        return best


def get_best_move_minimax(board, depth, ai_player=AI, human_player=PLAYER):
    counter = [0]
    best_val = -float('inf')
    best_move = None

    moves = order_moves(board, get_candidate_moves(board), ai_player, human_player)
    for r, c in moves:
        board[r][c] = ai_player
        val = _minimax(board, depth - 1, False, (r, c), ai_player, human_player, counter)
        board[r][c] = EMPTY
        if val > best_val:
            best_val = val
            best_move = (r, c)
        if best_val >= SCORE_WIN:
            break

    return best_move, best_val, counter[0]
