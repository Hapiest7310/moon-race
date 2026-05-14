SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Moon Race"

COLOR_BACKGROUND = (0, 0, 0)

FRAME_WIDTH = 64
FRAME_HEIGHT = 64
FRAME_COUNT = 32
ANIMATION_SPEED_MS = 80

MOON_SPRITESHEET = "assets/images/MOON.png"
MOON_SCALE = 2.0

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 70

GRID_CELL_SIZE = 32
GRID_COLS = SCREEN_WIDTH // GRID_CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // GRID_CELL_SIZE

debug = True
debug_mouse = True
debug_grid = True
debug_widgets = True
debug_fps = True
debug_app = True
debug_spinner = True
debug_hover = True
debug_cells = True
debug_layout = True
debug_menu = True

_fps = 0


def set_fps(v):
    global _fps
    _fps = v


def get_fps():
    return _fps


def get_screen_center():
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2


def get_button_start_position():
    return SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2


def get_moon_position():
    scaled_h = int(FRAME_HEIGHT * MOON_SCALE)
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - scaled_h // 2 - BUTTON_HEIGHT - BUTTON_SPACING
