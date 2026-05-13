# core/constants.py

# Board
BOARD_SIZE = 15
WIN_LENGTH = 4

# Players
EMPTY = 0
PLAYER = 1
AI = 2

# Difficulty
EASY = "Easy"
MEDIUM = "Medium"

# Screen
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750
CELL_SIZE = 44
BOARD_OFFSET_X = 60
BOARD_OFFSET_Y = 60
BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE

# Colors — dark modern palette
COLOR_BG         = (18, 18, 28)
COLOR_BOARD_BG   = (24, 24, 38)
COLOR_GRID       = (45, 45, 65)
COLOR_HOVER      = (80, 80, 120, 120)
COLOR_PLAYER     = (100, 200, 255)
COLOR_AI         = (255, 100, 120)
COLOR_WIN_LINE   = (255, 215, 0)
COLOR_TEXT       = (220, 220, 240)
COLOR_TEXT_DIM   = (120, 120, 160)
COLOR_ACCENT     = (100, 120, 255)
COLOR_HUD_BG     = (28, 28, 45)
COLOR_PANEL_BG   = (22, 22, 36)
COLOR_BTN        = (50, 55, 100)
COLOR_BTN_HOVER  = (70, 80, 140)
COLOR_BTN_TEXT   = (220, 220, 255)
COLOR_GREEN      = (80, 200, 120)
COLOR_YELLOW     = (255, 200, 60)
COLOR_RED        = (255, 80, 100)

# Fonts
FONT_TITLE_SIZE  = 52
FONT_LARGE_SIZE  = 28
FONT_MEDIUM_SIZE = 20
FONT_SMALL_SIZE  = 15

# AI Score table
SCORE_WIN     = 100000
SCORE_3       = 10000
SCORE_BLOCK3  = 7000
SCORE_2       = 1500

# Difficulty configs
DIFFICULTY_CONFIGS = {
    EASY:   {"algorithm": "Minimax",          "depth": 3},
    MEDIUM: {"algorithm": "Alpha-Beta",        "depth": 4},
}

# FPS
FPS = 60
