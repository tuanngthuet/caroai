# ui/hud/hud_panel.py
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    BOARD_SIZE, CELL_SIZE,
    COLOR_HUD_BG, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_ACCENT,
    COLOR_PLAYER, COLOR_AI, COLOR_GREEN, COLOR_YELLOW, COLOR_RED,
    PLAYER, AI, FONT_MEDIUM_SIZE, FONT_SMALL_SIZE
)

HUD_X = BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE + 24
HUD_Y = BOARD_OFFSET_Y
HUD_W = SCREEN_WIDTH - HUD_X - 16
HUD_H = SCREEN_HEIGHT - 40

class HUDPanel:
    def __init__(self, font_medium, font_small):
        self.fm = font_medium
        self.fs = font_small
        self.x = HUD_X
        self.y = HUD_Y
        self.w = HUD_W
        self.h = HUD_H

    def draw(self, surface, state):
        # Panel background
        panel_rect = pygame.Rect(self.x - 8, self.y - 8, self.w + 16, self.h + 16)
        pygame.draw.rect(surface, COLOR_HUD_BG, panel_rect, border_radius=10)
        pygame.draw.rect(surface, (50, 55, 90), panel_rect, 1, border_radius=10)

        y = self.y + 10
        line_h = 28

        def label(text, color=COLOR_TEXT_DIM, font=None):
            nonlocal y
            f = font or self.fs
            surf = f.render(text, True, color)
            surface.blit(surf, (self.x, y))
            y += line_h

        def value(key, val, key_color=COLOR_TEXT_DIM, val_color=COLOR_TEXT):
            nonlocal y
            ks = self.fs.render(key, True, key_color)
            vs = self.fs.render(str(val), True, val_color)
            surface.blit(ks, (self.x, y))
            surface.blit(vs, (self.x + self.w - vs.get_width() - 4, y))
            y += line_h

        def separator():
            nonlocal y
            pygame.draw.line(surface, (45, 45, 70),
                             (self.x, y), (self.x + self.w - 8, y))
            y += 10

        # Title
        title = self.fm.render("CARO AI", True, COLOR_ACCENT)
        surface.blit(title, (self.x + (self.w - title.get_width()) // 2, y))
        y += 38

        separator()

        # Difficulty
        value("Difficulty:", state.difficulty, val_color=COLOR_YELLOW)
        value("Algorithm:", state.agent_name if hasattr(state, 'agent_name') else "—")
        value("Depth:", state.last_depth if state.last_depth else "—")

        separator()

        # Current turn
        turn_color = COLOR_PLAYER if state.current_turn == PLAYER else COLOR_AI
        turn_text = "Player (X)" if state.current_turn == PLAYER else "AI (O)"
        value("Turn:", turn_text, val_color=turn_color)
        value("Move #:", state.move_count)

        separator()

        # AI stats
        label("AI Statistics", COLOR_ACCENT, self.fs)
        value("Nodes:", f"{state.nodes_explored:,}")
        value("Time:", f"{state.last_ai_time:.3f}s")
        value("Score:", state.last_eval_score)

        separator()

        # Game status
        if state.winner:
            if state.winner == PLAYER:
                label("Player Wins!", COLOR_GREEN, self.fm)
            else:
                label("AI Wins!", COLOR_AI, self.fm)
        elif state.is_draw:
            label("Draw!", COLOR_YELLOW, self.fm)
        else:
            label("Game in progress...", COLOR_TEXT_DIM)
