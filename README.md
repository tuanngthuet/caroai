# Caro AI Game

**Python + Pygame · Minimax · Alpha-Beta Pruning · Advanced Heuristic Search**

## Quick Start

```bash
pip install pygame
python main.py
```

## Features

| Feature | Details |
|---|---|
| Board | 15×15, win with 5 in a row |
| Easy AI | Minimax, depth 2 |
| Medium AI | Alpha-Beta Pruning, depth 3 |
| Benchmark | AI vs AI match with node/time stats |
| UI | Dark modern theme, hover effects, win animation |

## Project Structure

```
caro_game/
├── main.py                   # Entry point
├── core/                     # Constants, game state
├── game/                     # Board rules, game manager
├── ai/
│   ├── agents/               # EasyAgent, MediumAgent, 
│   ├── algorithms/           # minimax, alphabeta, advanced_alphabeta
│   ├── evaluation/           # basic_eval, advanced_eval
│   ├── heuristics/           # move_ordering
│   └── utils/                # node_counter
├── ui/
│   ├── menu/                 # MainMenu
│   ├── screens/              # GameScreen, BenchmarkScreen
│   ├── components/           # EndPopup
│   ├── animations/           # AnimationManager
│   ├── renderer/             # BoardRenderer
│   └── hud/                  # HUDPanel
└── benchmark/                # run_benchmark_suite
```

## Controls

- **Click** a cell to place your piece (X)
- AI (O) responds automatically
- Use the **← Menu** button to return to main menu
- Use **↩ Restart** to reset the current game

## AI Architecture

### Easy (Minimax, depth 2)
Pure Minimax — no pruning. Slow on large boards but simple reference implementation.

### Medium (Alpha-Beta, depth 3)
Classic Alpha-Beta pruning. Cuts branches when `β ≤ α`, visiting far fewer nodes.

### Hard (Advanced Alpha-Beta, depth 4)
Move ordering (winning moves first → blocking → center), heuristic candidate filtering (radius 2), and the advanced evaluation function with center-proximity bonus.

## Evaluation Function

| Pattern | Score |
|---|---|
| 5 AI pieces | +100,000 |
| 4 AI pieces | +10,000 |
| 3 AI pieces | +1,000 |
| 2 AI pieces | +100 |
| 4 human pieces | −9,000 |
| 3 human pieces | −800 |

## Benchmark

Open the game → click **Benchmark** to run:
- Easy vs Medium
- Medium vs Hard  
- Easy vs Hard

Stats displayed: avg nodes explored, avg time per move, winner.
