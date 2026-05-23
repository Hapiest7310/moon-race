"""
building_sprites.py — Loads and caches scaled building sprites from Buildings.png.

Usage:
    import src.building_sprites as building_sprites
    building_sprites.load("assets/images/Buildings.png")

    surf = building_sprites.get("House")   # returns a scaled Surface or None
"""

import pygame
from src import config

_sheet: pygame.Surface | None = None
_cache: dict[str, pygame.Surface] = {}


def load(path: str) -> None:
    """Load the spritesheet. Call once at level init."""
    global _sheet, _cache
    try:
        _sheet = pygame.image.load(path).convert_alpha()
        _cache = {}
        _preload_all()
        print(f"[SPRITES] Building sheet loaded: {path}")
    except FileNotFoundError:
        print(f"[SPRITES] WARNING: Buildings.png not found at {path} — using colored rects")
        _sheet = None


def _preload_all() -> None:
    for bt in config.BUILDING_TYPES:
        name = bt["name"]
        rect_tuple = bt.get("sprite_rect")
        if rect_tuple and _sheet:
            x1, y1, x2, y2 = rect_tuple
            crop_w = x2 - x1
            crop_h = y2 - y1
            if crop_w <= 0 or crop_h <= 0:
                continue
            # Target pixel size = grid footprint
            target_w = bt["w"] * config.GRID_CELL_SIZE
            target_h = bt["h"] * config.GRID_CELL_SIZE
            try:
                cropped = _sheet.subsurface(pygame.Rect(x1, y1, crop_w, crop_h))
                scaled = pygame.transform.smoothscale(cropped, (target_w, target_h))
                _cache[name] = scaled
            except ValueError as e:
                print(f"[SPRITES] Bad rect for {name}: {e}")


def get(name: str) -> pygame.Surface | None:
    """Return a cached scaled surface for a building name, or None if unavailable."""
    return _cache.get(name)


def is_loaded() -> bool:
    return _sheet is not None