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
    global _sheet, _cache
    import os
    print(f"[SPRITES] cwd: {os.getcwd()}")
    print(f"[SPRITES] file exists: {os.path.isfile(path)}")
    try:
        _sheet = pygame.image.load(path).convert_alpha()
        print(f"[SPRITES] sheet loaded, size: {_sheet.get_size()}")
        _cache = {}
        _preload_all()
        print(f"[SPRITES] cache keys: {list(_cache.keys())}")
    except FileNotFoundError:
        print(f"[SPRITES] WARNING: not found at {path}")
        _sheet = None
    except Exception as e:
        print(f"[SPRITES] ERROR: {e}")
        _sheet = None


def _preload_all() -> None:
    for bt in config.BUILDING_TYPES:
        name = bt["name"]
        rect_tuple = bt.get("sprite_rect")
        print(f"[SPRITES] processing {name}: sprite_rect={rect_tuple}")
        if rect_tuple and _sheet:
            x1, y1, x2, y2 = rect_tuple
            crop_w = x2 - x1
            crop_h = y2 - y1
            target_w = bt["w"] * config.GRID_CELL_SIZE
            target_h = bt["h"] * config.GRID_CELL_SIZE
            try:
                cropped = _sheet.subsurface(pygame.Rect(x1, y1, crop_w, crop_h))
                scaled = pygame.transform.smoothscale(cropped, (target_w, target_h))
                _cache[name] = scaled
                print(f"[SPRITES] ✓ {name} cached at {target_w}x{target_h}")
            except ValueError as e:
                print(f"[SPRITES] ✗ Bad rect for {name}: {e}")

def get(name: str) -> pygame.Surface | None:
    """Return a cached scaled surface for a building name, or None if unavailable."""
    return _cache.get(name)


def is_loaded() -> bool:
    return _sheet is not None