# benchmark/benchmark_runner.py
import time
from core.constants import BOARD_SIZE, EMPTY, PLAYER, AI, WIN_LENGTH, EASY, MEDIUM
from game.rules import check_winner
from ai.agents.minimax import Minimax
from ai.agents.alphabetapuring import AlphaBeta

AGENTS = {EASY: Minimax, MEDIUM: AlphaBeta}

class BenchmarkResult:
    def __init__(self, agent1_name, agent2_name):
        self.agent1_name = agent1_name
        self.agent2_name = agent2_name
        self.winner = None
        self.total_moves = 0
        self.agent1_stats = {"total_nodes": 0, "total_time": 0.0, "moves": 0}
        self.agent2_stats = {"total_nodes": 0, "total_time": 0.0, "moves": 0}
        self.is_draw = False

    def summary(self):
        def avg(s):
            m = s["moves"]
            return {
                "avg_nodes": s["total_nodes"]//max(1,m),
                "avg_time": s["total_time"]/max(1,m)
            }
        return {
            "agent1": self.agent1_name,
            "agent2": self.agent2_name,
            "winner": self.winner,
            "is_draw": self.is_draw,
            "total_moves": self.total_moves,
            "agent1_stats": avg(self.agent1_stats),
            "agent2_stats": avg(self.agent2_stats),
        }

def run_ai_vs_ai(diff1, diff2, max_moves=150):
    """Run one AI vs AI match. AI player = AI token, human = PLAYER token."""
    board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    agent1 = AGENTS[diff1]()  # plays as AI
    agent2 = AGENTS[diff2]()  # plays as PLAYER

    result = BenchmarkResult(diff1, diff2)
    move_count = 0
    current = AI  # agent1 goes first

    while move_count < max_moves:
        if current == AI:
            move, score, nodes, elapsed, depth = agent1.get_move(board, AI, PLAYER)
            player_token = AI
            stats = result.agent1_stats
        else:
            move, score, nodes, elapsed, depth = agent2.get_move(board, PLAYER, AI)
            player_token = PLAYER
            stats = result.agent2_stats

        if move is None:
            result.is_draw = True
            break

        r, c = move
        board[r][c] = player_token
        stats["total_nodes"] += nodes
        stats["total_time"] += elapsed
        stats["moves"] += 1
        move_count += 1
        result.total_moves = move_count

        winner, _ = check_winner(board, (r, c))
        if winner:
            result.winner = diff1 if winner == AI else diff2
            break

        # Check full board
        if all(board[r][c] != EMPTY for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
            result.is_draw = True
            break

        current = PLAYER if current == AI else AI

    return result


def run_benchmark_suite(callback=None):
    """Run all benchmark matchups, calling callback(result_dict) for each."""
    matchups = [
        (EASY, MEDIUM)
    ]
    results = []
    for d1, d2 in matchups:
        if callback:
            callback(f"Running {d1} vs {d2}...")
        r = run_ai_vs_ai(d1, d2, max_moves=80)
        results.append(r.summary())
        if callback:
            callback(r.summary())
    return results
