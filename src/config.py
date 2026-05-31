import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
GROUND_LAYERS = 6

STARTING_MONEY = 1000
SAVE_DIR = "saves"

BUILDING_TYPES = [
    {
        "name": "Ground",
        "w": 1,
        "h": 1,
        "cost": 0,
        "color": (255, 255, 255),
        "indestructible": True,
    },
    {
        "name": "Foundation",
        "w": 1,
        "h": 1,
        "cost": 10,
        "color": (139, 90, 43),
        "sprite_rect": (275, 710, 325, 750),
    },
    {
        "name": "Wall",
        "w": 2,
        "h": 1,
        "cost": 50,
        "color": (100, 100, 100),
        "sprite_rect": (600, 631, 700, 680),
    },
    {
        "name": "Tower",
        "w": 1,
        "h": 2,
        "cost": 50,
        "color": (70, 70, 90),
        "sprite_rect": (190, 695, 235, 750),
    },
    {
        "name": "House",
        "w": 2,
        "h": 2,
        "cost": 100,
        "color": (160, 82, 45),
        "sprite_rect": (695, 255, 765, 330),
    },
    {
        "name": "Workshop",
        "w": 2,
        "h": 3,
        "cost": 200,
        "color": (180, 120, 60),
        "sprite_rect": (270, 765, 335, 830),
    },
    {
        "name": "Mansion",
        "w": 3,
        "h": 3,
        "cost": 300,
        "color": (100, 149, 237),
        "sprite_rect": (640, 700, 750, 760),
    },
    {
        "name": "Palace",
        "w": 4,
        "h": 4,
        "cost": 500,
        "color": (218, 165, 32),
        "sprite_rect": (360, 705, 495, 830),
    },
    {
        "name": "Observatory",
        "w": 2,
        "h": 4,
        "cost": 400,
        "color": (147, 112, 219),
        "sprite_rect": (430, 433, 490, 553),
    },
    {
        "name": "green_house",
        "w": 4,
        "h": 2,
        "cost": 450,
        "color": (34, 139, 34),
        "sprite_rect": (355, 945, 505, 1000),
    },
]

MUSIC_DIR = "music"

LIGHT_MUSIC = "/home/serv/Desktop/ISE/music/light.mp3"
DARK_MUSIC = "/home/serv/Desktop/ISE/music/dark.mp3"

AUDIO_ENABLED = True
DEFAULT_MUSIC_VOLUME = 0.5
DEFAULT_SFX_VOLUME = 0.7

DROP_ANIMATION_MS = 500

# ── debug ──────────────────────────────────────────────────────────────
debug = False
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
debug_cat_state = True
debug_cat_manual = True
DEBUG_PRINT_INTERVAL = 500

ENABLE_GLSL = False

DARK_COUNTDOWN_SECONDS = 3
DARK_MINING_SECONDS = 60

# ── dark_2 (alien evasion) ─────────────────────────────────────────────
DARK2_PLAYER_RADIUS = 20
DARK2_PLAYER_ACCEL = 1600.0
DARK2_PLAYER_MAX_SPEED = 200.0
DARK2_PLAYER_FRICTION = 0.85

DARK2_ENEMY_RADIUS = 10
DARK2_ENEMY_BASE_SPEED = 90.0
DARK2_ENEMY_SPAWN_INTERVAL = 5000
DARK2_ENEMY_GROW_INTERVAL = 10000
DARK2_ENEMY_GROW_MAX_RADIUS = 20

DARK2_DIFFICULTY_RATE = 0.15
DARK2_DIFFICULTY_MAX_MULTIPLIER = 3.0
DARK2_COINS_PER_SECOND = 10

DARK2_PLAYER_LIVES = 3
DARK2_SPAWN_MARGIN = 80
DARK2_SPAWN_MIN_PLAYER_DIST = 200
DARK2_PREDICT_OFFSET = 200.0
DARK2_STAR_COUNT = 160
DARK2_SHAKE_HIT = 4
DARK2_BLINK_DURATION = 500

DARK2_BULLET_RADIUS = 3
DARK2_BULLET_SPEED = 350.0
DARK2_BULLET_LIFETIME = 3000

# ── move: dash ──────────────────────────────────────────────────────────
DARK2_MOVE_DASH_DISTANCE = 250
DARK2_MOVE_DASH_CHANCE = 0.015
DARK2_MOVE_DASH_COOLDOWN = 4000
DARK2_MOVE_DASH_WINDUP_MS = 500
DARK2_MOVE_DASH_SPEED = 800.0
DARK2_MOVE_DASH_DURATION_MS = 300

# ── move: shoot_bullets ─────────────────────────────────────────────────
DARK2_MOVE_SHOOT_CHANCE = 0.01
DARK2_MOVE_SHOOT_COOLDOWN = 5000
DARK2_MOVE_SHOOT_WINDUP_MS = 400
DARK2_MOVE_SHOOT_COUNT = 3
DARK2_MOVE_SHOOT_SPREAD = 0.3

# ── move: explode ───────────────────────────────────────────────────────
DARK2_MOVE_EXPLODE_CHANCE = 0.005
DARK2_MOVE_EXPLODE_COOLDOWN = 8000
DARK2_MOVE_EXPLODE_BLINKS = 3
DARK2_MOVE_EXPLODE_BLINK_INTERVAL_MS = 400
DARK2_MOVE_EXPLODE_BULLET_COUNT = 8

# ── move: attract ───────────────────────────────────────────────────────
DARK2_MOVE_ATTRACT_CHANCE = 0.008
DARK2_MOVE_ATTRACT_COOLDOWN = 6000
DARK2_MOVE_ATTRACT_SPEED = 250.0

# ── cat ────────────────────────────────────────────────────────────────
CAT_SPRITES_DIR = "assets/images/cat"
CAT_SCALE = 1.5
CAT_START_X = 200
CAT_GRAVITY = 1200.0
CAT_WALK_SPEED = 180.0
CAT_JUMP_VELOCITY = -480.0
CAT_ANIM_FPS = {
    "idle_1": 4,
    "idle_2": 4,
    "run_1": 8,
    "run_2": 8,
    "jump": 8,
    "hiss": 8,
    "lick_1": 4,
    "lick_2": 4,
    "punch": 6,
    "sleep": 4,
}
cheat_coins = True
show_grid = False

_fps = 0
_save_name = "default"
_mine_requested = False
_alien_requested = False


def set_fps(v):
    """Store the current FPS value."""
    global _fps
    _fps = v


def get_fps():
    """Return the stored FPS value."""
    return _fps


def set_save_name(name):
    """Set the name of the active save file."""
    global _save_name
    _save_name = name


def get_save_name():
    """Return the active save file name."""
    return _save_name


def set_mine_requested(v):
    """Set the flag to request the mining minigame."""
    global _mine_requested
    _mine_requested = v


def get_mine_requested():
    """Return whether the mining minigame was requested."""
    return _mine_requested


def clear_mine_requested():
    """Reset the mining minigame request flag."""
    global _mine_requested
    _mine_requested = False


def set_alien_requested(v):
    """Set the flag to request the alien evasion minigame."""
    global _alien_requested
    _alien_requested = v


def get_alien_requested():
    """Return whether the alien evasion minigame was requested."""
    return _alien_requested


def clear_alien_requested():
    """Reset the alien evasion minigame request flag."""
    global _alien_requested
    _alien_requested = False


def get_moon_position():
    """Calculate the centred screen position for the moon sprite."""
    scaled_h = int(FRAME_HEIGHT * MOON_SCALE)
    return (
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 - scaled_h // 2 - BUTTON_HEIGHT - BUTTON_SPACING,
    )


def generate_ground_layers():
    """Generate the initial ground tile layout for the grid."""
    cols = list(range(GRID_COLS))
    buildings = []
    for layer in range(min(GROUND_LAYERS, GRID_ROWS)):
        for gx in cols:
            buildings.append({"type": "Ground", "gx": gx, "gy": layer})
        if len(cols) <= 1:
            break
        random.shuffle(cols)
        cols = cols[:max(len(cols) // 2, 1)]
    return buildings
