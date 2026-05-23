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

DROP_ANIMATION_MS = 500

ENABLE_GLSL = False

DARK_COUNTDOWN_SECONDS = 3
DARK_MINING_SECONDS = 60

# ── cat ────────────────────────────────────────────────────────────────
CAT_SPRITES_DIR = "assets/images/cat"
CAT_SCALE = 1.5
CAT_START_X = 200
CAT_RUN_SPEED = 2
CAT_JUMP_HEIGHT = 40
CAT_JUMP_FRAMES = 30
CAT_IDLE_DURATION_RANGE = (2000, 6000)
CAT_RUN_DURATION_RANGE = (3000, 8000)
CAT_HISS_DURATION_RANGE = (1000, 3000)
CAT_ANIM_FPS = {
    "idle_1": 4, "idle_2": 4,
    "run_1": 8, "run_2": 8,
    "jump": 8,
    "hiss": 8, "lick_1": 4, "lick_2": 4,
    "punch": 6, "sleep": 4,
}
CAT_TRANSITIONS = {
    "idle":  {"run": 55, "jump": 15, "climb": 10, "idle": 20},
    "run":   {"idle": 45, "jump": 20, "climb": 5, "run": 30},
    "jump":  {"idle": 50, "run": 50},
    "climb": {"idle": 60, "run": 40},
}

# movement on the grid (pixels per second)
CAT_GRID_SPEED = 120
# vertical jump overshoot fraction (extra above target height)
CAT_JUMP_OVERSHOOT_FACTOR = 0.25
# time per grid row when climbing vertically (ms)
CAT_CLIMB_MS_PER_ROW = 120
# cat debug flags
debug_cat_plan = True
debug_cat_state = True
# allow manual setting of cat target block (debug)
debug_cat_manual_target = True

cheat_coins = True
show_grid = False

_fps = 0
_save_name = "default"
_mine_requested = False


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


def set_mine_requested(v):
    global _mine_requested
    _mine_requested = v


def get_mine_requested():
    return _mine_requested


def clear_mine_requested():
    global _mine_requested
    _mine_requested = False


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
