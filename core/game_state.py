# core/game_state.py
from core.constants import BOARD_SIZE, EMPTY, PLAYER, AI, EASY

class GameState:
    def __init__(self):
        self.board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_turn = PLAYER
        self.difficulty = EASY
        self.winner = None
        self.is_draw = False
        self.winning_cells = []
        self.last_move = None
        self.move_count = 0
        # AI stats
        self.nodes_explored = 0
        self.last_ai_time = 0.0
        self.last_eval_score = 0
        self.last_depth = 0

    def reset(self):
        self.__init__()
        self.difficulty = self.difficulty  # preserve

    def copy(self):
        gs = GameState()
        gs.board = [row[:] for row in self.board]
        gs.current_turn = self.current_turn
        gs.difficulty = self.difficulty
        gs.winner = self.winner
        gs.is_draw = self.is_draw
        gs.winning_cells = self.winning_cells[:]
        gs.last_move = self.last_move
        gs.move_count = self.move_count
        return gs

    def place(self, r, c, player):
        if self.board[r][c] == EMPTY:
            self.board[r][c] = player
            self.last_move = (r, c)
            self.move_count += 1
            return True
        return False

    def undo(self, r, c):
        self.board[r][c] = EMPTY
        self.move_count -= 1

    def is_full(self):
        return all(self.board[r][c] != EMPTY
                   for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))
