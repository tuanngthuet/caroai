import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_HUD_BG, COLOR_TEXT, COLOR_ACCENT,
    COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_TEXT, COLOR_TEXT_DIM,
    COLOR_PLAYER, COLOR_AI, COLOR_GREEN,
)
from ui.menu.main_menu import Button

ALGORITHMS = ["Minimax", "Alpha-Beta"]
DEPTHS = [1, 2, 3, 4, 5]
MATCH_COUNTS = [1, 3, 5, 10]


class _AgentConfig:
    """Holds UI state for one agent column."""

    def __init__(self, x, y, label, fonts, default_algo=0, default_depth=2):
        self.label = label
        self.algo_idx = default_algo
        self.depth_idx = default_depth  # index into DEPTHS
        self.fonts = fonts
        self.x = x
        self.y = y
        col_w = 220

        btn_w, btn_h = 36, 30
        # Algorithm toggle buttons
        self.algo_btns = []
        for i, name in enumerate(ALGORITHMS):
            bx = x + i * (col_w // len(ALGORITHMS))
            self.algo_btns.append(Button((bx, y + 60, col_w // len(ALGORITHMS) - 6, btn_h),
                                         name, fonts['small']))

        # Depth toggle buttons
        self.depth_btns = []
        for i, d in enumerate(DEPTHS):
            bx = x + i * (btn_w + 6)
            self.depth_btns.append(Button((bx, y + 130, btn_w, btn_h),
                                           str(d), fonts['small']))

    def handle_event(self, event):
        for i, btn in enumerate(self.algo_btns):
            if btn.clicked(event):
                self.algo_idx = i
        for i, btn in enumerate(self.depth_btns):
            if btn.clicked(event):
                self.depth_idx = i

    def update(self, mouse_pos):
        for btn in self.algo_btns:
            btn.update(mouse_pos)
        for btn in self.depth_btns:
            btn.update(mouse_pos)

    def draw(self, surface):
        # Column header
        lbl = self.fonts['medium'].render(self.label, True, COLOR_ACCENT)
        surface.blit(lbl, (self.x, self.y + 20))

        algo_lbl = self.fonts['small'].render("Algorithm:", True, COLOR_TEXT_DIM)
        surface.blit(algo_lbl, (self.x, self.y + 42))
        for i, btn in enumerate(self.algo_btns):
            btn.draw(surface, selected=(i == self.algo_idx))

        depth_lbl = self.fonts['small'].render("Depth:", True, COLOR_TEXT_DIM)
        surface.blit(depth_lbl, (self.x, self.y + 112))
        for i, btn in enumerate(self.depth_btns):
            btn.draw(surface, selected=(i == self.depth_idx))

    def get_cfg(self):
        algo = ALGORITHMS[self.algo_idx]
        depth = DEPTHS[self.depth_idx]
        label = f"{algo.lower().replace('-','').replace(' ','_')}_d{depth}"
        return {"label": label, "config": {"algorithm": algo, "depth": depth}}


class BenchmarkConfigScreen:
    def __init__(self, surface, fonts):
        self.surface = surface
        self.fonts = fonts

        col_y = 160
        self.agent_x = _AgentConfig(120, col_y, "Agent X  (plays first)", fonts,
                                     default_algo=0, default_depth=2)
        self.agent_o = _AgentConfig(600, col_y, "Agent O  (plays second)", fonts,
                                     default_algo=1, default_depth=3)

        # Match count selector
        self.match_idx = 1  # default = MATCH_COUNTS[1] = 3
        self.match_btns = []
        bx0 = SCREEN_WIDTH // 2 - (len(MATCH_COUNTS) * 66) // 2
        for i, n in enumerate(MATCH_COUNTS):
            self.match_btns.append(Button((bx0 + i * 66, 380, 58, 34),
                                           str(n), fonts['small']))

        self.btn_back = Button((20, 20, 120, 38), "← Menu", fonts['small'])
        self.btn_run = Button((SCREEN_WIDTH // 2 - 120, 450, 240, 48),
                               "▶  Run Benchmark", fonts['medium'])

    def handle_event(self, event):
        if self.btn_back.clicked(event):
            return "menu"
        self.agent_x.handle_event(event)
        self.agent_o.handle_event(event)
        for i, btn in enumerate(self.match_btns):
            if btn.clicked(event):
                self.match_idx = i
        if self.btn_run.clicked(event):
            return ("run", self.agent_x.get_cfg(), self.agent_o.get_cfg(),
                    MATCH_COUNTS[self.match_idx])
        return None

    def update(self, mouse_pos):
        self.btn_back.update(mouse_pos)
        self.btn_run.update(mouse_pos)
        self.agent_x.update(mouse_pos)
        self.agent_o.update(mouse_pos)
        for btn in self.match_btns:
            btn.update(mouse_pos)

    def draw(self):
        self.surface.fill(COLOR_BG)

        title = self.fonts['large'].render("BENCHMARK CONFIGURATION", True, COLOR_ACCENT)
        self.surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Divider between agents
        pygame.draw.line(self.surface, (45, 45, 80),
                         (SCREEN_WIDTH // 2, 150), (SCREEN_WIDTH // 2, 340), 1)

        self.agent_x.draw(self.surface)
        self.agent_o.draw(self.surface)

        # Match count
        mc_lbl = self.fonts['medium'].render("Number of matches:", True, COLOR_TEXT_DIM)
        self.surface.blit(mc_lbl, (SCREEN_WIDTH // 2 - mc_lbl.get_width() // 2, 348))
        for i, btn in enumerate(self.match_btns):
            btn.draw(self.surface, selected=(i == self.match_idx))

        self.btn_back.draw(self.surface)
        self.btn_run.draw(self.surface)
