import pygame
from src import config
from src.sprites import AnimatedSprite

_active = False
_moon = None
_font = None
_caption = ""


def init():
    global _moon, _font
    cx = config.SCREEN_WIDTH // 2
    cy = config.SCREEN_HEIGHT // 2
    scaled_h = int(config.FRAME_HEIGHT * config.MOON_SCALE)
    _moon = AnimatedSprite(
        x=cx, y=cy - scaled_h // 2 - 20,
        animation_speed=60
    )
    _font = pygame.font.Font(None, 40)


def start(caption="Loading..."):
    global _active, _caption
    _active = True
    _caption = caption
    if config.debug and config.debug_spinner:
        print(f'[SPINNER] start "{caption}"')


def stop():
    global _active
    _active = False
    if config.debug and config.debug_spinner:
        print("[SPINNER] stop")


def is_active():
    return _active


def update(dt):
    if _active and _moon:
        _moon.update(dt)


def draw(surface):
    if not (_active and _moon and _font):
        return
    surface.fill(config.COLOR_BACKGROUND)
    surface.blit(_moon.image, _moon.rect)
    text = _font.render(_caption, True, (180, 180, 255))
    tx = config.SCREEN_WIDTH // 2 - text.get_width() // 2
    ty = _moon.rect.bottom + 30
    surface.blit(text, (tx, ty))
