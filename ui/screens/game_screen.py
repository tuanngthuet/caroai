# ui/screens/game_screen.py
import pygame
import threading
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    COLOR_BG, COLOR_TEXT, COLOR_ACCENT, COLOR_BTN, COLOR_BTN_HOVER, COLOR_BTN_TEXT,
    COLOR_TEXT_DIM, PLAYER, AI, EASY, MEDIUM,
    FONT_MEDIUM_SIZE, FONT_SMALL_SIZE, COLOR_RED
)
from game.game_manager import GameManager
from ui.renderer.board_renderer import BoardRenderer
from ui.animations.animator import AnimationManager
from ui.hud.hud_panel import HUDPanel
from ui.components.end_popup import EndPopup
from ui.menu.main_menu import Button

class GameScreen:
    def __init__(self, surface, fonts, difficulty=EASY):
        self.surface = surface
        self.fonts = fonts
        self.difficulty = difficulty
        self.manager = GameManager(difficulty)
        self.renderer = BoardRenderer(surface)
        self.anim = AnimationManager()
        self.hud = HUDPanel(fonts['medium'], fonts['small'])
        self.popup = EndPopup(fonts)
        self.hover_cell = None
        self.ai_thread = None
        self.ai_lock = threading.Lock()

        # Back button
        self.btn_back = Button((14, 14, 110, 36), "← Menu", fonts['small'])
        self.btn_restart = Button((134, 14, 110, 36), "Restart", fonts['small'])
        self.btn_undo = Button((254, 14, 90, 36), "Undo", fonts['small'])

        # Enrich state with agent name
        self._update_agent_name()

    def _update_agent_name(self):
        from core.constants import DIFFICULTY_CONFIGS
        cfg = DIFFICULTY_CONFIGS[self.difficulty]
        self.manager.state.agent_name = cfg["algorithm"]

    def handle_event(self, event):
        action = self.popup.handle_event(event)
        if action == "replay":
            self._restart()
            return None
        if action == "menu":
            return "menu"

        if self.btn_back.clicked(event):
            return "menu"
        if self.btn_restart.clicked(event):
            self._restart()
            return None
        if self.btn_undo.clicked(event):
            self._undo()
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.manager.state.current_turn == PLAYER and not self.manager.state.winner and not self.manager.state.is_draw:
                r, c = self.renderer.pixel_to_board(*event.pos)
                if r is not None:
                    if self.manager.player_move(r, c):
                        self.anim.add_piece(r, c, PLAYER, CELL_SIZE,
                                             BOARD_OFFSET_X, BOARD_OFFSET_Y)
                        self._check_end()
                        if not self.manager.state.winner and not self.manager.state.is_draw:
                            self._start_ai_thread()
        return None

    def update(self, dt, mouse_pos):
        self.btn_back.update(mouse_pos)
        self.btn_restart.update(mouse_pos)
        self.btn_undo.update(mouse_pos)
        self.popup.update(mouse_pos)
        self.anim.update(dt)

        # Hover
        r, c = self.renderer.pixel_to_board(*mouse_pos)
        if r is not None and self.manager.state.board[r][c] == 0:
            self.hover_cell = (r, c)
        else:
            self.hover_cell = None

        # AI move done?
        if self.ai_thread and not self.ai_thread.is_alive():
            self.ai_thread = None
            last = self.manager.state.last_move
            if last:
                self.anim.add_piece(last[0], last[1], AI, CELL_SIZE,
                                     BOARD_OFFSET_X, BOARD_OFFSET_Y)
            self._check_end()

    def draw(self):
        self.surface.fill(COLOR_BG)
        state = self.manager.state

        # Board
        self.renderer.draw_background()
        self.renderer.draw_grid()
        self.renderer.draw_hover(self.hover_cell, state.board)
        self.renderer.draw_pieces(state.board, self.anim, state.winning_cells)

        if state.winning_cells:
            self.renderer.draw_win_line(state.winning_cells)

        # HUD
        self.hud.draw(self.surface, state)

        # AI thinking indicator
        if self.ai_thread and self.ai_thread.is_alive():
            dot = self.fonts['small'].render("AI thinking...", True, COLOR_ACCENT)
            self.surface.blit(dot, (BOARD_OFFSET_X + 4, BOARD_OFFSET_Y - 28))

        # Buttons
        self.btn_back.draw(self.surface)
        self.btn_restart.draw(self.surface)
        self.btn_undo.draw(self.surface)

        # Popup
        self.popup.draw(self.surface)

    def _start_ai_thread(self):
        self._ai_start_time = __import__('time').time()
        self.ai_thread = threading.Thread(target=self._ai_worker, daemon=True)
        self.ai_thread.start()

    def _ai_worker(self):
        with self.ai_lock:
            self.manager.ai_move()
        self.manager.state.last_ai_time = __import__('time').time() - self._ai_start_time

    def _check_end(self):
        state = self.manager.state
        if state.winner:
            self.anim.set_win(state.winning_cells)
            self.popup.show(state.winner, False)
        elif state.is_draw:
            self.popup.show(None, True)

    def _restart(self):
        self.manager.reset()
        self.anim.reset()
        self.popup.hide()
        self._update_agent_name()
        self.ai_thread = None

    def _undo(self):
        if self.ai_thread and self.ai_thread.is_alive():
            return  # AI is thinking, can't undo
        if self.manager.undo_last_round():
            self.anim.reset()
            self.popup.hide()
