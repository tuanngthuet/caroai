import time
import json
from core.constants import BOARD_SIZE, EMPTY, AI, PLAYER
from game.rules import check_winner
from ai.algorithms.minimax import get_best_move_minimax
from ai.algorithms.alphabeta import get_best_move_alphabeta

ALGORITHMS = {
    "Minimax":    get_best_move_minimax,
    "Alpha-Beta": get_best_move_alphabeta,
}


def _make_agent_fn(config):
    """Return a callable (board, ai_player, human_player) -> (move, score, nodes, elapsed, depth)."""
    algo_fn = ALGORITHMS[config["algorithm"]]
    depth = config["depth"]

    def agent_fn(board, ai_player, human_player):
        start = time.time()
        move, score, nodes = algo_fn([row[:] for row in board], depth, ai_player, human_player)
        return move, score, nodes, time.time() - start, depth

    return agent_fn


def run_custom_match(cfg_x, cfg_y, game_index, n_games, move_callback=None):
    """
    Run one AI vs AI game.
    cfg_x / cfg_y: {"label": str, "config": {"algorithm": str, "depth": int}}
    move_callback(dict) is called after every move with live progress info.
    """
    label_x = cfg_x["label"]
    label_y = cfg_y["label"]
    fn_x = _make_agent_fn(cfg_x["config"])
    fn_y = _make_agent_fn(cfg_y["config"])

    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    current = AI   # X goes first (AI token)
    move_count = 0
    winner_label = None
    is_draw = False

    while move_count < 150:
        if current == AI:
            move, _, nodes, elapsed, depth = fn_x(board, AI, PLAYER)
            token = AI
            mover = label_x
        else:
            move, _, nodes, elapsed, depth = fn_y(board, PLAYER, AI)
            token = PLAYER
            mover = label_y

        if move is None:
            is_draw = True
            break

        r, c = move
        board[r][c] = token
        move_count += 1

        if move_callback:
            move_callback({
                "type": "move",
                "game_index": game_index,
                "move_count": move_count,
                "mover": mover,
                "move": (r, c),
                "nodes": nodes,
                "elapsed": elapsed,
                "board": [row[:] for row in board],
            })

        w, _ = check_winner(board, (r, c))
        if w:
            winner_label = label_x if w == AI else label_y
            break

        if all(board[i][j] != EMPTY for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)):
            is_draw = True
            break

        current = PLAYER if current == AI else AI

    if is_draw:
        winner_label = "draw"
        result_x = result_y = "draw"
    else:
        result_x = "win" if winner_label == label_x else "loss"
        result_y = "win" if winner_label == label_y else "loss"

    match_id = f"{label_x}_vs_{label_y}__game_{game_index}"

    # Build final board string
    symbols = {EMPTY: ".", AI: "X", PLAYER: "O"}
    board_lines = ["Final board:"]
    for row in board:
        board_lines.append(" ".join(symbols[v] for v in row))
    board_str = "\n".join(board_lines)

    agent_x_json = json.dumps({
        "label": label_x,
        "config": {
            "depth": cfg_x["config"]["depth"],
            "algorithm": cfg_x["config"]["algorithm"],
            "use_cython_search": False,
            "use_tss": False,
            "use_lazy_smp": False,
            "beam_width_root": 0,
            "beam_width_inner": 0,
            "move_time_budget_sec": 20,
        }
    })
    agent_y_json = json.dumps({
        "label": label_y,
        "config": {
            "depth": cfg_y["config"]["depth"],
            "algorithm": cfg_y["config"]["algorithm"],
            "use_cython_search": False,
            "use_tss": False,
            "use_lazy_smp": False,
            "beam_width_root": 0,
            "beam_width_inner": 0,
            "move_time_budget_sec": 20,
        }
    })

    output = (
        f"completion_index={game_index}\n"
        f"game_seq={game_index}\n"
        f"match_id={match_id}\n"
        f"winner={winner_label}\n"
        f"agent_x={agent_x_json}\n"
        f"agent_o={agent_y_json}\n"
        f"result_for_agent_x={result_x}\n"
        f"result_for_agent_o={result_y}\n"
        f"{board_str}"
    )

    return {
        "output": output,
        "winner": winner_label,
        "result_x": result_x,
        "result_y": result_y,
        "match_id": match_id,
        "game_index": game_index,
        "label_x": label_x,
        "label_y": label_y,
    }


def run_custom_suite(cfg_x, cfg_y, n_games, callback=None, move_callback=None):
    """Run n_games matches between cfg_x and cfg_y, calling callback(game_result) after each."""
    results = []
    for i in range(1, n_games + 1):
        if callback:
            callback({"status": "running", "game_index": i, "n_games": n_games})
        r = run_custom_match(cfg_x, cfg_y, i, n_games, move_callback=move_callback)
        results.append(r)
        if callback:
            callback(r)
    return results
