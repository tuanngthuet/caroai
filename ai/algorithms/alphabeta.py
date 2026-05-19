# ai/algorithms/alphabeta.py
from random import Random

from core.constants import AI, PLAYER, SCORE_WIN, EMPTY, BOARD_SIZE
from game.rules import check_winner, get_candidate_moves
from ai.evaluation.evaluation import evaluate_board
from ai.heuristics.move_ordering import order_moves

_ZOBRIST_KEYS = None
_ZOBRIST_RANDOM = Random(0xC0FFEE)


def _init_zobrist():
    global _ZOBRIST_KEYS
    if _ZOBRIST_KEYS is None:
        _ZOBRIST_KEYS = [
            [[_ZOBRIST_RANDOM.getrandbits(64) for _ in range(2)] for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]
    return _ZOBRIST_KEYS


def _hash_board(board):
    zob = _init_zobrist()
    h = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == AI:
                h ^= zob[r][c][0]
            elif board[r][c] == PLAYER:
                h ^= zob[r][c][1]
    return h


def _hash_move(board_hash, r, c, player):
    zob = _init_zobrist()
    index = 0 if player == AI else 1
    return board_hash ^ zob[r][c][index]


def _alphabeta(board, depth, alpha, beta, is_maximizing, last_move,
               ai_player, human_player, counter, board_hash, transposition_table):
    counter[0] += 1

    winner, _ = check_winner(board, last_move)
    if winner == ai_player:
        return SCORE_WIN + depth      # faster win = higher score
    if winner == human_player:
        return -(SCORE_WIN + depth)   # faster loss = lower score

    if depth == 0:
        return evaluate_board(board, last_move, ai_player, human_player)

    entry = transposition_table.get(board_hash)
    if entry and entry["depth"] >= depth:
        if entry["flag"] == "EXACT":
            return entry["value"]
        elif entry["flag"] == "LOWER":
            alpha = max(alpha, entry["value"])
        elif entry["flag"] == "UPPER":
            beta = min(beta, entry["value"])
        if alpha >= beta:
            return entry["value"]

    moves = order_moves(board, get_candidate_moves(board), ai_player, human_player)
    if not moves:
        return 0

    original_alpha = alpha
    original_beta = beta
    best = -float('inf') if is_maximizing else float('inf')

    if is_maximizing:
        for r, c in moves:
            board[r][c] = ai_player
            child_hash = _hash_move(board_hash, r, c, ai_player)
            val = _alphabeta(board, depth - 1, alpha, beta, False,
                             (r, c), ai_player, human_player,
                             counter, child_hash, transposition_table)
            board[r][c] = EMPTY
            if val > best:
                best = val
            alpha = max(alpha, best)
            if alpha >= beta:
                break   # β-cutoff
    else:
        for r, c in moves:
            board[r][c] = human_player
            child_hash = _hash_move(board_hash, r, c, human_player)
            val = _alphabeta(board, depth - 1, alpha, beta, True,
                             (r, c), ai_player, human_player,
                             counter, child_hash, transposition_table)
            board[r][c] = EMPTY
            if val < best:
                best = val
            beta = min(beta, best)
            if alpha >= beta:
                break   # α-cutoff

    if best <= original_alpha:
        flag = "UPPER"
    elif best >= original_beta:
        flag = "LOWER"
    else:
        flag = "EXACT"
    transposition_table[board_hash] = {"value": best, "depth": depth, "flag": flag}

    return best


def get_best_move_alphabeta(board, depth, ai_player=AI, human_player=PLAYER):
    """
    Iterative deepening alpha-beta: search depth 1..depth, using the
    previous iteration's best move first for better pruning.
    """
    counter = [0]
    best_move = None
    best_val = -float('inf')
    transposition_table = {}
    board_hash = _hash_board(board)

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
            child_hash = _hash_move(board_hash, r, c, ai_player)
            val = _alphabeta(board, d - 1, alpha, beta, False,
                             (r, c), ai_player, human_player,
                             counter, child_hash, transposition_table)
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
