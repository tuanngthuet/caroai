# ui/screens/benchmark_screen.py
import pygame
import threading
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_HUD_BG,
    COLOR_TEXT, COLOR_ACCENT, COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_TEXT,
    COLOR_TEXT_DIM, COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_AI, COLOR_PLAYER,
    EASY, MEDIUM
)
from benchmark.benchmark_runner import run_benchmark_suite
from ui.menu.main_menu import Button

class BenchmarkScreen:
    def __init__(self, surface, fonts):
        self.surface = surface
        self.fonts = fonts
        self.running = False
        self.done = False
        self.log = []
        self.results = []
        self.thread = None

        self.btn_back = Button((20, 20, 120, 38), "← Menu", fonts['small'])
        self.btn_run = Button((SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT - 70, 220, 44),
                              "▶  Run Benchmark", fonts['medium'])

    def handle_event(self, event):
        if self.btn_back.clicked(event):
            return "menu"
        if self.btn_run.clicked(event) and not self.running:
            self._start()
        return None

    def update(self, dt, mouse_pos):
        self.btn_back.update(mouse_pos)
        self.btn_run.update(mouse_pos)
        if self.thread and not self.thread.is_alive():
            self.thread = None
            self.running = False
            self.done = True

    def draw(self):
        self.surface.fill(COLOR_BG)

        title = self.fonts['large'].render("BENCHMARK MODE", True, COLOR_ACCENT)
        self.surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))

        sub = self.fonts['small'].render("AI vs AI — comparing Minimax, Alpha-Beta, and Advanced Alpha-Beta",
                                          True, COLOR_TEXT_DIM)
        self.surface.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 75))

        y = 110
        for line in self.log[-20:]:
            if isinstance(line, dict):
                self._draw_result(y, line)
                y += 120
            else:
                txt = self.fonts['small'].render(str(line), True, COLOR_TEXT_DIM)
                self.surface.blit(txt, (60, y))
                y += 22

        if self.running:
            dot = self.fonts['medium'].render("Running...", True, COLOR_YELLOW)
            self.surface.blit(dot, (SCREEN_WIDTH//2 - dot.get_width()//2, SCREEN_HEIGHT//2))

        self.btn_back.draw(self.surface)
        if not self.running:
            self.btn_run.draw(self.surface)

    def _draw_result(self, y, r):
        w1 = 500
        panel = pygame.Rect(SCREEN_WIDTH//2 - w1//2, y, w1, 105)
        pygame.draw.rect(self.surface, COLOR_HUD_BG, panel, border_radius=8)
        pygame.draw.rect(self.surface, (50,50,90), panel, 1, border_radius=8)

        header = f"{r['agent1']} vs {r['agent2']}"
        ht = self.fonts['medium'].render(header, True, COLOR_TEXT)
        self.surface.blit(ht, (panel.x + 16, y + 10))

        if r['is_draw']:
            wt = self.fonts['small'].render("Result: Draw", True, COLOR_YELLOW)
        else:
            wt = self.fonts['small'].render(f"Winner: {r['winner']}", True, COLOR_GREEN)
        self.surface.blit(wt, (panel.x + 16, y + 38))

        a1 = r['agent1_stats']
        a2 = r['agent2_stats']
        s1 = f"{r['agent1']}: {a1['avg_nodes']:,} nodes  {a1['avg_time']:.3f}s/move"
        s2 = f"{r['agent2']}: {a2['avg_nodes']:,} nodes  {a2['avg_time']:.3f}s/move"
        t1 = self.fonts['small'].render(s1, True, COLOR_TEXT_DIM)
        t2 = self.fonts['small'].render(s2, True, COLOR_TEXT_DIM)
        self.surface.blit(t1, (panel.x + 16, y + 62))
        self.surface.blit(t2, (panel.x + 16, y + 82))

    def _start(self):
        self.running = True
        self.done = False
        self.log = ["Starting benchmark suite..."]
        self.results = []
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        def cb(data):
            self.log.append(data)
        run_benchmark_suite(callback=cb)
