# ai/agents/minimax.py
from ai.algorithms.minimax import get_best_move_minimax
from core.constants import EASY, DIFFICULTY_CONFIGS, AI, PLAYER
import time

class Minimax:
    name = EASY
    algorithm = "Minimax"

    def __init__(self):
        self.depth = DIFFICULTY_CONFIGS[EASY]["depth"]

    def get_move(self, board, ai_player=AI, human_player=PLAYER):
        start = time.time()
        move, score, nodes = get_best_move_minimax(
            [row[:] for row in board], self.depth, ai_player, human_player
        )
        elapsed = time.time() - start
        return move, score, nodes, elapsed, self.depth
