#!/usr/bin/env python3
# main.py — Caro AI Game
import pygame
import sys
import os

# Make sure imports work from project root
sys.path.insert(0, os.path.dirname(__file__))

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    FONT_TITLE_SIZE, FONT_LARGE_SIZE, FONT_MEDIUM_SIZE, FONT_SMALL_SIZE,
    COLOR_BG, EASY
)
from ui.menu.main_menu import MainMenu
from ui.screens.game_screen import GameScreen
from ui.screens.benchmark_screen import BenchmarkScreen


def load_fonts():
    pygame.font.init()
    try:
        # Try to use a nice system font
        candidates = ["segoeui", "arial", "helvetica", "dejavusans", "freesans"]
        font_name = None
        for c in candidates:
            if c in [f.lower() for f in pygame.font.get_fonts()]:
                font_name = c
                break
        return {
            'title':  pygame.font.SysFont(font_name, FONT_TITLE_SIZE, bold=True),
            'large':  pygame.font.SysFont(font_name, FONT_LARGE_SIZE, bold=True),
            'medium': pygame.font.SysFont(font_name, FONT_MEDIUM_SIZE),
            'small':  pygame.font.SysFont(font_name, FONT_SMALL_SIZE),
        }
    except Exception:
        return {
            'title':  pygame.font.Font(None, FONT_TITLE_SIZE),
            'large':  pygame.font.Font(None, FONT_LARGE_SIZE),
            'medium': pygame.font.Font(None, FONT_MEDIUM_SIZE),
            'small':  pygame.font.Font(None, FONT_SMALL_SIZE),
        }


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Caro AI — Python + Pygame")
    clock = pygame.time.Clock()

    fonts = load_fonts()

    # Screens
    current_screen = "menu"
    menu = MainMenu(fonts)
    game_screen = None
    bench_screen = None
    selected_difficulty = EASY

    while True:
        dt = clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if current_screen == "menu":
                action = menu.handle_event(event)
                if action:
                    if action[0] == "play":
                        selected_difficulty = action[1]
                        game_screen = GameScreen(screen, fonts, selected_difficulty)
                        current_screen = "game"
                    elif action[0] == "benchmark":
                        bench_screen = BenchmarkScreen(screen, fonts)
                        current_screen = "benchmark"
                    elif action[0] == "exit":
                        pygame.quit()
                        sys.exit()

            elif current_screen == "game":
                action = game_screen.handle_event(event)
                if action == "menu":
                    current_screen = "menu"
                    game_screen = None

            elif current_screen == "benchmark":
                action = bench_screen.handle_event(event)
                if action == "menu":
                    current_screen = "menu"
                    bench_screen = None

        # Update
        if current_screen == "menu":
            menu.update(mouse_pos)
        elif current_screen == "game" and game_screen:
            game_screen.update(dt, mouse_pos)
        elif current_screen == "benchmark" and bench_screen:
            bench_screen.update(dt, mouse_pos)

        # Draw
        if current_screen == "menu":
            menu.draw(screen)
        elif current_screen == "game" and game_screen:
            game_screen.draw()
        elif current_screen == "benchmark" and bench_screen:
            bench_screen.draw()

        pygame.display.flip()


if __name__ == "__main__":
    main()
