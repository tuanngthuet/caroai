# ai/agents/alphabetapuring.py
from ai.algorithms.alphabeta import get_best_move_alphabeta
from core.constants import MEDIUM, DIFFICULTY_CONFIGS, AI, PLAYER
import time

class AlphaBeta:
    name = MEDIUM
    algorithm = "Alpha-Beta"

    def __init__(self):
        self.depth = DIFFICULTY_CONFIGS[MEDIUM]["depth"]

    def get_move(self, board, ai_player=AI, human_player=PLAYER):
        start = time.time()
        move, score, nodes = get_best_move_alphabeta(
            [row[:] for row in board], self.depth, ai_player, human_player
        )
        elapsed = time.time() - start
        return move, score, nodes, elapsed, self.depth
