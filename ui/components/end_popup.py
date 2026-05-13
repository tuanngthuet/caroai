# ui/components/end_popup.py
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_HUD_BG, COLOR_TEXT, COLOR_ACCENT,
    COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_TEXT,
    COLOR_PLAYER, COLOR_AI, COLOR_GREEN, COLOR_YELLOW,
    PLAYER, AI, FONT_LARGE_SIZE, FONT_MEDIUM_SIZE
)

class EndPopup:
    def __init__(self, fonts):
        self.font_large = fonts['large']
        self.font_medium = fonts['medium']
        self.visible = False
        self.winner = None
        self.is_draw = False

        pw, ph = 400, 220
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        self.rect = pygame.Rect(px, py, pw, ph)

        bw, bh = 160, 44
        self.btn_replay = self._make_btn(px + 30, py + 150, bw, bh, "↩  Replay")
        self.btn_menu = self._make_btn(px + pw - 30 - bw, py + 150, bw, bh, "⌂  Menu")

    def _make_btn(self, x, y, w, h, text):
        return {"rect": pygame.Rect(x, y, w, h), "text": text, "hovered": False}

    def show(self, winner, is_draw):
        self.visible = True
        self.winner = winner
        self.is_draw = is_draw

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_replay["rect"].collidepoint(event.pos):
                return "replay"
            if self.btn_menu["rect"].collidepoint(event.pos):
                return "menu"
        return None

    def update(self, mouse_pos):
        if not self.visible:
            return
        for btn in [self.btn_replay, self.btn_menu]:
            btn["hovered"] = btn["rect"].collidepoint(mouse_pos)

    def draw(self, surface):
        if not self.visible:
            return

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(surface, COLOR_HUD_BG, self.rect, border_radius=14)
        pygame.draw.rect(surface, COLOR_ACCENT, self.rect, 2, border_radius=14)

        # Result text
        if self.is_draw:
            msg = "Draw!"
            color = COLOR_YELLOW
        elif self.winner == PLAYER:
            msg = "You Win! 🎉"
            color = COLOR_GREEN
        else:
            msg = "AI Wins!"
            color = COLOR_AI

        label = self.font_large.render(msg, True, color)
        surface.blit(label, (self.rect.centerx - label.get_width()//2, self.rect.y + 50))

        sub = self.font_medium.render("What next?", True, (150, 150, 190))
        surface.blit(sub, (self.rect.centerx - sub.get_width()//2, self.rect.y + 100))

        # Buttons
        for btn in [self.btn_replay, self.btn_menu]:
            color = COLOR_BTN_HOVER if btn["hovered"] else COLOR_BTN
            pygame.draw.rect(surface, color, btn["rect"], border_radius=8)
            txt = self.font_medium.render(btn["text"], True, COLOR_BTN_TEXT)
            surface.blit(txt, (btn["rect"].centerx - txt.get_width()//2,
                               btn["rect"].centery - txt.get_height()//2))
