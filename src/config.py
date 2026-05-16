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

STARTING_MONEY = 1000
SAVE_DIR = "saves"
SAVE_FILE = "light_side_save.json"

BUILDING_TYPES = [
    {"name": "Foundation", "w": 1, "h": 1, "cost": 10, "color": (139, 90, 43)},
    {"name": "Wall", "w": 2, "h": 1, "cost": 50, "color": (100, 100, 100)},
    {"name": "Tower", "w": 1, "h": 2, "cost": 50, "color": (70, 70, 90)},
    {"name": "House", "w": 2, "h": 2, "cost": 100, "color": (160, 82, 45)},
    {"name": "Workshop", "w": 3, "h": 2, "cost": 200, "color": (180, 120, 60)},
    {"name": "Mansion", "w": 3, "h": 3, "cost": 300, "color": (100, 149, 237)},
    {"name": "Palace", "w": 4, "h": 4, "cost": 500, "color": (218, 165, 32)},
    {"name": "Observatory", "w": 2, "h": 4, "cost": 400, "color": (147, 112, 219)},
]

MUSIC_DIR = "music"

AUDIO_ENABLED = True
DEFAULT_MUSIC_VOLUME = 0.5
DEFAULT_SFX_VOLUME = 0.7

debug = True
debug_mouse = True
debug_grid = False
debug_widgets = True
debug_fps = True
debug_app = True
debug_spinner = True
debug_hover = True
debug_cells = True
debug_layout = True
debug_menu = True
debug_audio = True

cheat_coins = True
show_grid = False

_fps = 0
_save_name = "default"


def set_fps(v):
    global _fps
    _fps = v


def get_fps():
    return _fps


def set_save_name(name):
    global _save_name
    _save_name = name


def get_save_name():
    return _save_name


def get_screen_center():
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2


def get_button_start_position():
    return SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, SCREEN_HEIGHT // 2


def get_moon_position():
    scaled_h = int(FRAME_HEIGHT * MOON_SCALE)
    return (
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 - scaled_h // 2 - BUTTON_HEIGHT - BUTTON_SPACING,
    )
