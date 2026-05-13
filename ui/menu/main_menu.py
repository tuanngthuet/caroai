# ui/menu/main_menu.py
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_TEXT,
    COLOR_TEXT_DIM, COLOR_PLAYER, COLOR_AI, COLOR_YELLOW,
    EASY, MEDIUM,
    FONT_TITLE_SIZE, FONT_LARGE_SIZE, FONT_MEDIUM_SIZE
)

class Button:
    def __init__(self, rect, text, font, color=COLOR_BTN, hover_color=COLOR_BTN_HOVER):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface, selected=False):
        color = self.hover_color if (self.hovered or selected) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        if selected:
            pygame.draw.rect(surface, COLOR_ACCENT, self.rect, 2, border_radius=8)
        label = self.font.render(self.text, True, COLOR_BTN_TEXT)
        lx = self.rect.centerx - label.get_width() // 2
        ly = self.rect.centery - label.get_height() // 2
        surface.blit(label, (lx, ly))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))


class MainMenu:
    def __init__(self, fonts):
        self.font_title = fonts['title']
        self.font_large = fonts['large']
        self.font_medium = fonts['medium']
        self.font_small = fonts['small']
        self.selected_difficulty = EASY

        cx = SCREEN_WIDTH // 2
        bw, bh = 240, 50
        bx = cx - bw // 2

        self.btn_play = Button((bx, 340, bw, bh), "PLAY", self.font_large)
        self.btn_benchmark = Button((bx, 410, bw, bh), "BENCHMARK", self.font_large)
        self.btn_exit = Button((bx, 480, bw, bh), "EXIT", self.font_large)

        dw, dh = 150, 42
        total = 3 * dw + 2 * 16
        dx0 = cx - total // 2

        self.diff_buttons = {
            EASY:   Button((dx0, 260, dw, dh), "Easy",   self.font_medium, color=(30,80,50), hover_color=(40,110,65)),
            MEDIUM: Button((dx0+dw+16, 260, dw, dh), "Medium", self.font_medium, color=(80,70,20), hover_color=(110,100,25)),
        }

    def handle_event(self, event):
        for diff, btn in self.diff_buttons.items():
            if btn.clicked(event):
                self.selected_difficulty = diff
                return None
        if self.btn_play.clicked(event):
            return ("play", self.selected_difficulty)
        if self.btn_benchmark.clicked(event):
            return ("benchmark", self.selected_difficulty)
        if self.btn_exit.clicked(event):
            return ("exit",)
        return None

    def update(self, mouse_pos):
        self.btn_play.update(mouse_pos)
        self.btn_benchmark.update(mouse_pos)
        self.btn_exit.update(mouse_pos)
        for btn in self.diff_buttons.values():
            btn.update(mouse_pos)

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # Title
        title = self.font_title.render("CARO AI", True, COLOR_ACCENT)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        sub = self.font_small.render("Python  ·  Pygame  ·  Minimax  ·  Alpha-Beta", True, COLOR_TEXT_DIM)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 148))

        # Decorative line
        pygame.draw.line(surface, (45, 45, 80),
                         (SCREEN_WIDTH//2 - 200, 175), (SCREEN_WIDTH//2 + 200, 175), 1)

        # Difficulty label
        dlabel = self.font_medium.render("Select Difficulty:", True, COLOR_TEXT_DIM)
        surface.blit(dlabel, (SCREEN_WIDTH//2 - dlabel.get_width()//2, 225))

        for diff, btn in self.diff_buttons.items():
            btn.draw(surface, selected=(diff == self.selected_difficulty))

        self.btn_play.draw(surface)
        self.btn_benchmark.draw(surface)
        self.btn_exit.draw(surface)

        # Footer
        footer = self.font_small.render("Click a cell to place your piece  ·  Win with 4 in a row", True, COLOR_TEXT_DIM)
        surface.blit(footer, (SCREEN_WIDTH//2 - footer.get_width()//2, SCREEN_HEIGHT - 40))
