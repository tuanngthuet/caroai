# ui/renderer/board_renderer.py
import pygame
import math
from core.constants import (
    BOARD_SIZE, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    EMPTY, PLAYER, AI,
    COLOR_BOARD_BG, COLOR_GRID, COLOR_PLAYER, COLOR_AI,
    COLOR_HOVER, COLOR_WIN_LINE, COLOR_BG
)

class BoardRenderer:
    def __init__(self, surface):
        self.surface = surface
        self.cell = CELL_SIZE
        self.ox = BOARD_OFFSET_X
        self.oy = BOARD_OFFSET_Y
        self.board_px = BOARD_SIZE * self.cell

    def board_to_pixel(self, r, c):
        return self.ox + c * self.cell, self.oy + r * self.cell

    def pixel_to_board(self, px, py):
        c = (px - self.ox) // self.cell
        r = (py - self.oy) // self.cell
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return r, c
        return None, None

    def draw_background(self):
        # Board background
        bg_rect = pygame.Rect(self.ox - 8, self.oy - 8,
                              self.board_px + 16, self.board_px + 16)
        pygame.draw.rect(self.surface, COLOR_BOARD_BG, bg_rect, border_radius=6)

    def draw_grid(self):
        for i in range(BOARD_SIZE + 1):
            x = self.ox + i * self.cell
            y = self.oy + i * self.cell
            pygame.draw.line(self.surface, COLOR_GRID,
                             (x, self.oy), (x, self.oy + self.board_px), 1)
            pygame.draw.line(self.surface, COLOR_GRID,
                             (self.ox, y), (self.ox + self.board_px, y), 1)

        # Star points (like Go board)
        stars = []
        s = [3, BOARD_SIZE//2, BOARD_SIZE-4]
        for sr in s:
            for sc in s:
                stars.append((sr, sc))
        for (sr, sc) in stars:
            px, py = self.board_to_pixel(sr, sc)
            pygame.draw.circle(self.surface, COLOR_GRID, (px + self.cell//2, py + self.cell//2), 3)

    def draw_hover(self, hover_cell, board):
        if hover_cell is None:
            return
        r, c = hover_cell
        if board[r][c] != EMPTY:
            return
        px, py = self.board_to_pixel(r, c)
        surf = pygame.Surface((self.cell, self.cell), pygame.SRCALPHA)
        surf.fill((100, 140, 255, 60))
        self.surface.blit(surf, (px, py))

    def draw_pieces(self, board, anim_manager, winning_cells):
        radius = self.cell // 2 - 4

        # Collect animated pieces
        anim_cells = {(a.r, a.c): a for a in anim_manager.get_piece_anims()}

        win_anim = anim_manager.get_win_anim()
        win_alpha = win_anim.get_alpha() if win_anim and not win_anim.done else 255

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece == EMPTY:
                    continue
                px, py = self.board_to_pixel(r, c)
                cx = px + self.cell // 2
                cy = py + self.cell // 2

                color = COLOR_PLAYER if piece == PLAYER else COLOR_AI

                if (r, c) in anim_cells:
                    a = anim_cells[(r, c)]
                    scale = a.get_scale()
                    r_draw = int(radius * scale)
                    alpha = a.get_alpha()
                else:
                    r_draw = radius
                    alpha = 255

                if (r, c) in [(wr, wc) for wr, wc in winning_cells]:
                    # Golden outline
                    pygame.draw.circle(self.surface, COLOR_WIN_LINE, (cx, cy), r_draw + 3)

                pygame.draw.circle(self.surface, color, (cx, cy), max(1, r_draw))

                # Inner shine
                shine_r = max(1, r_draw // 3)
                shine_x = cx - r_draw // 4
                shine_y = cy - r_draw // 4
                shine_color = tuple(min(255, v + 60) for v in color)
                pygame.draw.circle(self.surface, shine_color, (shine_x, shine_y), shine_r)

    def draw_win_line(self, winning_cells, win_alpha=220):
        if not winning_cells or len(winning_cells) < 2:
            return
        r1, c1 = winning_cells[0]
        r2, c2 = winning_cells[-1]
        px1, py1 = self.board_to_pixel(r1, c1)
        px2, py2 = self.board_to_pixel(r2, c2)
        cx1 = px1 + self.cell // 2
        cy1 = py1 + self.cell // 2
        cx2 = px2 + self.cell // 2
        cy2 = py2 + self.cell // 2
        pygame.draw.line(self.surface, COLOR_WIN_LINE, (cx1, cy1), (cx2, cy2), 5)
