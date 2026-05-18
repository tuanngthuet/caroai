# ui/screens/analysis_screen.py
import pygame
import threading
import time
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOARD_SIZE, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    EMPTY, PLAYER, AI,
    COLOR_BG, COLOR_HUD_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT,
    COLOR_PLAYER, COLOR_AI, COLOR_GREEN, COLOR_YELLOW, COLOR_WIN_LINE,
)
from ui.menu.main_menu import Button
from ui.renderer.board_renderer import BoardRenderer
from game.rules import check_winner
from ai.algorithms.minimax import get_best_move_minimax
from ai.algorithms.alphabeta import get_best_move_alphabeta

ALGORITHMS = {"Minimax": get_best_move_minimax, "Alpha-Beta": get_best_move_alphabeta}
DEPTHS = [1, 2, 3, 4, 5]
HUD_X = BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE + 24
HUD_W = SCREEN_WIDTH - HUD_X - 16


class AnalysisScreen:
    def __init__(self, surface, fonts):
        self.surface = surface
        self.fonts = fonts
        self.renderer = BoardRenderer(surface)

        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ai_side = AI
        self.algo_idx = 1
        self.depth_idx = 2
        self.winning_cells = []
        self.last_move = None
        self.last_nodes = 0
        self.last_time = 0.0
        self.last_score = 0
        self.status = "Edit board, then click ▶ Move"
        self.winner = None
        self.ai_thinking = False
        self.ai_thread = None
        self.hover_cell = None

        bx = HUD_X
        self.btn_back  = Button((14, 14, 110, 36), "← Menu", fonts['small'])
        self.btn_clear = Button((134, 14, 100, 36), "Clear",  fonts['small'])
        self.btn_side_x = Button((bx, 0, 80, 30), "X", fonts['small'])   # y set in draw
        self.btn_side_o = Button((bx + 88, 0, 80, 30), "O", fonts['small'])
        self.btn_algos  = [Button((bx, 0, 168, 30), name, fonts['small'])
                           for name in ALGORITHMS]
        self.btn_depths = [Button((bx + i * 34, 0, 30, 30), str(d), fonts['small'])
                           for i, d in enumerate(DEPTHS)]
        self.btn_move   = Button((bx, SCREEN_HEIGHT - 70, 168, 44), "▶  Move", fonts['medium'])

    # ------------------------------------------------------------------ #
    def handle_event(self, event):
        if self.btn_back.clicked(event):
            return "menu"
        if self.btn_clear.clicked(event):
            self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
            self.winning_cells = []
            self.last_move = None
            self.winner = None
            self.status = "Edit board, then click ▶ Move"

        if self.btn_side_x.clicked(event): self.ai_side = AI
        if self.btn_side_o.clicked(event): self.ai_side = PLAYER
        for i, btn in enumerate(self.btn_algos):
            if btn.clicked(event): self.algo_idx = i
        for i, btn in enumerate(self.btn_depths):
            if btn.clicked(event): self.depth_idx = i

        if self.btn_move.clicked(event) and not self.ai_thinking and not self.winner:
            self._trigger_ai_move()

        # Board left-click: cycle EMPTY→X→O→EMPTY; right-click: erase
        if event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
            r, c = self.renderer.pixel_to_board(*event.pos)
            if r is not None:
                if event.button == 1:
                    self.board[r][c] = {EMPTY: AI, AI: PLAYER, PLAYER: EMPTY}[self.board[r][c]]
                elif event.button == 3:
                    self.board[r][c] = EMPTY
        return None

    def update(self, dt, mouse_pos):
        for btn in [self.btn_back, self.btn_clear, self.btn_side_x, self.btn_side_o, self.btn_move]:
            btn.update(mouse_pos)
        for btn in self.btn_algos + self.btn_depths:
            btn.update(mouse_pos)
        r, c = self.renderer.pixel_to_board(*mouse_pos)
        self.hover_cell = (r, c) if r is not None else None
        if self.ai_thread and not self.ai_thread.is_alive():
            self.ai_thread = None
            self.ai_thinking = False

    def draw(self):
        self.surface.fill(COLOR_BG)
        self._draw_board()
        self._draw_hud()
        self.btn_back.draw(self.surface)
        self.btn_clear.draw(self.surface)

    # ------------------------------------------------------------------ #
    def _draw_board(self):
        self.renderer.draw_background()
        self.renderer.draw_grid()
        self.renderer.draw_hover(self.hover_cell, self.board)

        radius = CELL_SIZE // 2 - 4
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                v = self.board[r][c]
                if v == EMPTY:
                    continue
                px, py = self.renderer.board_to_pixel(r, c)
                cx, cy = px + CELL_SIZE // 2, py + CELL_SIZE // 2
                color = COLOR_AI if v == AI else COLOR_PLAYER
                if (r, c) in self.winning_cells:
                    pygame.draw.circle(self.surface, COLOR_WIN_LINE, (cx, cy), radius + 3)
                pygame.draw.circle(self.surface, color, (cx, cy), radius)
                if self.last_move == (r, c):
                    pygame.draw.circle(self.surface, COLOR_YELLOW, (cx, cy), radius + 4, 2)

        if self.winning_cells:
            self.renderer.draw_win_line(self.winning_cells)

    def _draw_hud(self):
        panel = pygame.Rect(HUD_X - 8, BOARD_OFFSET_Y - 8, HUD_W + 16, SCREEN_HEIGHT - BOARD_OFFSET_Y)
        pygame.draw.rect(self.surface, COLOR_HUD_BG, panel, border_radius=10)
        pygame.draw.rect(self.surface, (50, 55, 90), panel, 1, border_radius=10)

        bx, y = HUD_X, 60

        def text(s, color=COLOR_TEXT_DIM, font=None):
            nonlocal y
            surf = (font or self.fonts['small']).render(s, True, color)
            self.surface.blit(surf, (bx, y)); y += surf.get_height() + 4

        def sep():
            nonlocal y
            pygame.draw.line(self.surface, (45, 45, 70), (bx, y), (bx + HUD_W - 8, y)); y += 10

        def row(k, v, vc=COLOR_TEXT):
            nonlocal y
            ks = self.fonts['small'].render(k, True, COLOR_TEXT_DIM)
            vs = self.fonts['small'].render(str(v), True, vc)
            self.surface.blit(ks, (bx, y))
            self.surface.blit(vs, (bx + HUD_W - vs.get_width() - 4, y))
            y += 22

        text("ANALYSIS", COLOR_ACCENT, self.fonts['medium']); y += 4
        text("Left-click: cycle X/O/empty  |  Right: erase")
        sep()

        # AI side
        text("AI plays:"); 
        self.btn_side_x.rect.y = y; self.btn_side_o.rect.y = y
        self.btn_side_x.draw(self.surface, selected=(self.ai_side == AI))
        self.btn_side_o.draw(self.surface, selected=(self.ai_side == PLAYER))
        y += 38

        # Algorithm
        text("Algorithm:")
        for i, btn in enumerate(self.btn_algos):
            btn.rect.y = y; y += 36
            btn.draw(self.surface, selected=(i == self.algo_idx))
        y += 4

        # Depth
        text("Depth:")
        for btn in self.btn_depths:
            btn.rect.y = y
        for i, btn in enumerate(self.btn_depths):
            btn.draw(self.surface, selected=(i == self.depth_idx))
        y += 38

        sep()

        # Stats
        if self.last_move:
            row("Last move:", f"({self.last_move[0]}, {self.last_move[1]})", COLOR_YELLOW)
            row("Nodes:", f"{self.last_nodes:,}")
            row("Time:", f"{self.last_time:.3f}s")
            row("Score:", self.last_score)
            sep()

        status_color = COLOR_GREEN if self.winner else (COLOR_YELLOW if self.ai_thinking else COLOR_TEXT_DIM)
        text(self.status, status_color)

        if not self.winner:
            self.btn_move.draw(self.surface)

    # ------------------------------------------------------------------ #
    def _trigger_ai_move(self):
        self.ai_thinking = True
        self.status = "Thinking…"
        self.ai_thread = threading.Thread(target=self._ai_worker, daemon=True)
        self.ai_thread.start()

    def _ai_worker(self):
        algo_fn = list(ALGORITHMS.values())[self.algo_idx]
        depth = DEPTHS[self.depth_idx]
        human = PLAYER if self.ai_side == AI else AI

        t0 = time.time()
        move, score, nodes = algo_fn([row[:] for row in self.board], depth, self.ai_side, human)
        elapsed = time.time() - t0

        if move is None:
            self.status = "No moves available"
            self.ai_thinking = False
            return

        r, c = move
        self.board[r][c] = self.ai_side
        self.last_move = (r, c)
        self.last_nodes = nodes
        self.last_time = elapsed
        self.last_score = score

        winner, cells = check_winner(self.board, (r, c))
        if winner:
            self.winner = winner
            self.winning_cells = cells
            self.status = f"{'X' if winner == AI else 'O'} wins!"
        else:
            self.status = f"Moved ({r}, {c}) — click ▶ Move again"

        self.ai_thinking = False
