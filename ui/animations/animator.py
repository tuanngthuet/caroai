# ui/animations/animator.py
import pygame
import math

class PiecePlacementAnim:
    """Scale-in + fade-in when a piece is placed."""
    def __init__(self, r, c, player, cell_size, offset_x, offset_y, duration=0.25):
        self.r = r
        self.c = c
        self.player = player
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.duration = duration
        self.elapsed = 0.0
        self.done = False

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.done = True

    def get_scale(self):
        t = min(self.elapsed / self.duration, 1.0)
        # ease out cubic
        return 1 - (1 - t) ** 3

    def get_alpha(self):
        return int(255 * min(self.elapsed / self.duration, 1.0))

class WinFlashAnim:
    """Flash winning cells gold."""
    def __init__(self, cells, duration=2.0, flash_speed=6.0):
        self.cells = cells
        self.duration = duration
        self.flash_speed = flash_speed
        self.elapsed = 0.0
        self.done = False

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.done = True

    def get_alpha(self):
        t = self.elapsed * self.flash_speed
        return int(127 + 127 * math.sin(t))

class AnimationManager:
    def __init__(self):
        self.piece_anims = []
        self.win_anim = None

    def add_piece(self, r, c, player, cell_size, ox, oy):
        self.piece_anims.append(PiecePlacementAnim(r, c, player, cell_size, ox, oy))

    def set_win(self, cells):
        self.win_anim = WinFlashAnim(cells)

    def update(self, dt):
        self.piece_anims = [a for a in self.piece_anims if not a.done]
        for a in self.piece_anims:
            a.update(dt)
        if self.win_anim and not self.win_anim.done:
            self.win_anim.update(dt)

    def reset(self):
        self.piece_anims = []
        self.win_anim = None

    def get_piece_anims(self):
        return self.piece_anims

    def get_win_anim(self):
        return self.win_anim
