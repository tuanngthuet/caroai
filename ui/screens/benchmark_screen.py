import pygame
import threading
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_HUD_BG,
    COLOR_TEXT, COLOR_ACCENT, COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_TEXT,
    COLOR_TEXT_DIM, COLOR_GREEN, COLOR_YELLOW, COLOR_RED,
    COLOR_PLAYER, COLOR_AI, BOARD_SIZE, EMPTY, AI, PLAYER,
)
from benchmark.benchmark_runner import run_custom_suite
from ui.screens.benchmark_config_screen import BenchmarkConfigScreen
from ui.menu.main_menu import Button

# Live board display constants
_CELL = 28          # px per cell
_BOARD_PX = BOARD_SIZE * _CELL
_BOARD_X = SCREEN_WIDTH // 2 - _BOARD_PX // 2
_BOARD_Y = 110


class BenchmarkScreen:
    def __init__(self, surface, fonts):
        self.surface = surface
        self.fonts = fonts
        self._show_config()

    # ------------------------------------------------------------------ #
    def _show_config(self):
        self.phase = "config"
        self.config_screen = BenchmarkConfigScreen(self.surface, self.fonts)

    def _start_run(self, cfg_x, cfg_o, n_games):
        self.phase = "running"          # live board view while game plays
        self.cfg_x = cfg_x
        self.cfg_o = cfg_o
        self.n_games = n_games
        self.game_results = []
        self.running = True
        self.done = False
        self.scroll = 0
        self._lines_cache = []

        # Live progress state (written by worker thread, read by draw)
        self._live = {
            "board": [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)],
            "game_index": 1,
            "move_count": 0,
            "mover": "",
            "last_move": None,
            "nodes": 0,
            "elapsed": 0.0,
        }

        self.btn_back = Button((20, 20, 120, 38), "← Menu", self.fonts['small'])
        self.btn_again = Button((SCREEN_WIDTH - 160, 20, 140, 38), "↩ Again", self.fonts['small'])

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    # ------------------------------------------------------------------ #
    def handle_event(self, event):
        if self.phase == "config":
            action = self.config_screen.handle_event(event)
            if action == "menu":
                return "menu"
            if isinstance(action, tuple) and action[0] == "run":
                _, cfg_x, cfg_o, n_games = action
                self._start_run(cfg_x, cfg_o, n_games)
            return None

        if self.btn_back.clicked(event):
            return "menu"
        if self.phase == "results" and self.btn_again.clicked(event) and self.done:
            self._show_config()
            return None
        if self.phase == "results" and event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y * 3)
        return None

    def update(self, dt, mouse_pos):
        if self.phase == "config":
            self.config_screen.update(mouse_pos)
            return
        self.btn_back.update(mouse_pos)
        self.btn_again.update(mouse_pos)
        if self.thread and not self.thread.is_alive():
            self.thread = None
            self.running = False
            self.done = True
            self.phase = "results"

    def draw(self):
        if self.phase == "config":
            self.config_screen.draw()
            return
        if self.phase == "running":
            self._draw_live()
        else:
            self._draw_results()

    # ------------------------------------------------------------------ #
    def _draw_live(self):
        self.surface.fill(COLOR_BG)
        live = self._live

        # Header
        hdr = self.fonts['medium'].render(
            f"Game {live['game_index']} / {self.n_games}  —  Move {live['move_count']}",
            True, COLOR_ACCENT)
        self.surface.blit(hdr, (SCREEN_WIDTH // 2 - hdr.get_width() // 2, 20))

        # Agent labels
        lx = self.fonts['small'].render(
            f"X: {self.cfg_x['label']}", True, COLOR_AI)
        lo = self.fonts['small'].render(
            f"O: {self.cfg_o['label']}", True, COLOR_PLAYER)
        self.surface.blit(lx, (SCREEN_WIDTH // 2 - lx.get_width() // 2 - 120, 55))
        self.surface.blit(lo, (SCREEN_WIDTH // 2 - lo.get_width() // 2 + 120, 55))

        # Current mover
        if live["mover"]:
            mt = self.fonts['small'].render(
                f"Thinking: {live['mover']}  |  nodes: {live['nodes']:,}  |  {live['elapsed']:.3f}s",
                True, COLOR_YELLOW)
            self.surface.blit(mt, (SCREEN_WIDTH // 2 - mt.get_width() // 2, 78))

        # Board
        board = live["board"]
        symbols = {EMPTY: None, AI: "X", PLAYER: "O"}
        colors  = {AI: COLOR_AI, PLAYER: COLOR_PLAYER}

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = _BOARD_X + c * _CELL
                y = _BOARD_Y + r * _CELL
                cell_rect = pygame.Rect(x, y, _CELL, _CELL)
                pygame.draw.rect(self.surface, (30, 30, 48), cell_rect)
                pygame.draw.rect(self.surface, (50, 50, 75), cell_rect, 1)

                v = board[r][c]
                if v != EMPTY:
                    # Highlight last move
                    if live["last_move"] == (r, c):
                        pygame.draw.rect(self.surface, (60, 60, 100), cell_rect)
                    label = self.fonts['small'].render(symbols[v], True, colors[v])
                    self.surface.blit(label, (
                        x + _CELL // 2 - label.get_width() // 2,
                        y + _CELL // 2 - label.get_height() // 2,
                    ))

        # Progress bar (moves out of 150 max)
        bar_w = _BOARD_PX
        bar_x = _BOARD_X
        bar_y = _BOARD_Y + _BOARD_PX + 10
        filled = int(bar_w * live["move_count"] / 150)
        pygame.draw.rect(self.surface, (40, 40, 65), (bar_x, bar_y, bar_w, 8), border_radius=4)
        pygame.draw.rect(self.surface, COLOR_ACCENT, (bar_x, bar_y, filled, 8), border_radius=4)

        self.btn_back.draw(self.surface)

    # ------------------------------------------------------------------ #
    def _draw_results(self):
        self.surface.fill(COLOR_BG)

        hdr = self.fonts['large'].render("BENCHMARK RESULTS", True, COLOR_ACCENT)
        self.surface.blit(hdr, (SCREEN_WIDTH // 2 - hdr.get_width() // 2, 28))

        sub = f"{self.cfg_x['label']}  vs  {self.cfg_o['label']}  ·  {self.n_games} game(s)"
        st = self.fonts['small'].render(sub, True, COLOR_TEXT_DIM)
        self.surface.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, 68))

        self.btn_back.draw(self.surface)
        if self.done:
            self.btn_again.draw(self.surface)

        area_top, area_bottom, line_h = 100, SCREEN_HEIGHT - 20, 18
        clip = pygame.Rect(0, area_top, SCREEN_WIDTH, area_bottom - area_top)
        self.surface.set_clip(clip)

        y = area_top - self.scroll * line_h
        for line in self._lines_cache:
            if area_top <= y < area_bottom:
                surf = self.fonts['small'].render(line, True, self._line_color(line))
                self.surface.blit(surf, (40, y))
            y += line_h

        self.surface.set_clip(None)

        total = len(self._lines_cache)
        visible = (area_bottom - area_top) // line_h
        if total > visible:
            max_scroll = total - visible
            self.scroll = min(self.scroll, max_scroll)
            bar_h = max(20, int(visible / total * (area_bottom - area_top)))
            bar_y = area_top + int(self.scroll / max_scroll * (area_bottom - area_top - bar_h))
            pygame.draw.rect(self.surface, (60, 60, 100),
                             (SCREEN_WIDTH - 10, bar_y, 6, bar_h), border_radius=3)

    # ------------------------------------------------------------------ #
    def _line_color(self, line):
        if line.startswith("winner=") or line.startswith("result_for_agent"):
            return COLOR_GREEN
        if line.startswith("match_id=") or line.startswith("==="):
            return COLOR_ACCENT
        if line.startswith("agent_"):
            return COLOR_TEXT_DIM
        return COLOR_TEXT

    def _worker(self):
        def on_move(data):
            # Update live state for the board view
            self._live.update({
                "board":      data["board"],
                "game_index": data["game_index"],
                "move_count": data["move_count"],
                "mover":      data["mover"],
                "last_move":  data["move"],
                "nodes":      data["nodes"],
                "elapsed":    data["elapsed"],
            })

        def on_game(data):
            if isinstance(data, dict) and "output" in data:
                self.game_results.append(data)
                self._lines_cache.append(f"=== Game {data['game_index']} / {self.n_games} ===")
                self._lines_cache.extend(data["output"].splitlines())
                self._lines_cache.append("")
                self.scroll = max(0, len(self._lines_cache) - 30)

        run_custom_suite(self.cfg_x, self.cfg_o, self.n_games,
                         callback=on_game, move_callback=on_move)
