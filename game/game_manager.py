# game/game_manager.py
from core.constants import PLAYER, AI, EASY, MEDIUM
from core.game_state import GameState
from game.rules import check_winner, is_valid
from ai.agents.minimax import Minimax
from ai.agents.alphabetapuring import AlphaBeta

AGENT_MAP = {EASY: Minimax, MEDIUM: AlphaBeta}

class GameManager:
    def __init__(self, difficulty=EASY):
        self.state = GameState()
        self.state.difficulty = difficulty
        self.agent = AGENT_MAP[difficulty]()
        self.ai_thinking = False

    def set_difficulty(self, difficulty):
        self.state.difficulty = difficulty
        self.agent = AGENT_MAP[difficulty]()

    def reset(self):
        difficulty = self.state.difficulty
        self.state = GameState()
        self.state.difficulty = difficulty
        self.agent = AGENT_MAP[difficulty]()
        self.ai_thinking = False

    def player_move(self, r, c):
        if self.state.winner or self.state.is_draw:
            return False
        if self.state.current_turn != PLAYER:
            return False
        if not is_valid(self.state.board, r, c):
            return False

        self.state.place(r, c, PLAYER)
        winner, cells = check_winner(self.state.board, (r, c))
        if winner:
            self.state.winner = winner
            self.state.winning_cells = cells
        elif self.state.is_full():
            self.state.is_draw = True
        else:
            self.state.current_turn = AI
        return True

    def ai_move(self):
        if self.state.winner or self.state.is_draw:
            return False
        if self.state.current_turn != AI:
            return False

        board_copy = [row[:] for row in self.state.board]
        move, score, nodes, elapsed, depth = self.agent.get_move(board_copy)

        if move is None:
            return False

        r, c = move
        self.state.place(r, c, AI)
        self.state.nodes_explored = nodes
        self.state.last_ai_time = elapsed
        self.state.last_eval_score = score
        self.state.last_depth = depth

        winner, cells = check_winner(self.state.board, (r, c))
        if winner:
            self.state.winner = winner
            self.state.winning_cells = cells
        elif self.state.is_full():
            self.state.is_draw = True
        else:
            self.state.current_turn = PLAYER
        return True
