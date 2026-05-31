"""
building_sprites.py — Loads and caches scaled building sprites from Buildings.png.

Usage:
    import src.animations.building_sprites as building_sprites
    building_sprites.load("assets/images/Buildings.png")

    surf = building_sprites.get("House")   # returns a scaled Surface or None
"""

import pygame
from src import config

_sheet: pygame.Surface | None = None
_cache: dict[str, pygame.Surface] = {}


def load(path: str) -> None:
    """Load the building sprite sheet and pre-cache all building surfaces."""
    global _sheet, _cache
    import os
    if config.debug:
        print(f"[SPRITES] cwd: {os.getcwd()}")
        print(f"[SPRITES] file exists: {os.path.isfile(path)}")
    try:
        _sheet = pygame.image.load(path).convert_alpha()
        if config.debug:
            print(f"[SPRITES] sheet loaded, size: {_sheet.get_size()}")
        _cache = {}
        _preload_all()
        if config.debug:
            print(f"[SPRITES] cache keys: {list(_cache.keys())}")
    except FileNotFoundError:
        if config.debug:
            print(f"[SPRITES] WARNING: not found at {path}")
        _sheet = None
    except Exception as e:
        if config.debug:
            print(f"[SPRITES] ERROR: {e}")
        _sheet = None


def _remove_dark_background(surface: pygame.Surface, threshold: int = 60) -> pygame.Surface:
    """Make only the dark navy background pixels transparent, preserving building details."""
    result = surface.copy().convert_alpha()
    arr = pygame.surfarray.pixels3d(result)
    alpha = pygame.surfarray.pixels_alpha(result)

    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)

    # Target the specific dark background: low overall brightness
    # AND blue channel not dramatically higher than red/green (avoids removing blue building parts)
    brightness = (r + g + b) / 3
    dark_mask = (brightness < threshold)

    alpha[dark_mask] = 0

    del arr, alpha
    return result


def _preload_all() -> None:
    """Extract and cache a scaled surface for every building type."""
    for bt in config.BUILDING_TYPES:
        name = bt["name"]
        rect_tuple = bt.get("sprite_rect")
        if config.debug:
            print(f"[SPRITES] processing {name}: sprite_rect={rect_tuple}")
        if rect_tuple and _sheet:
            x1, y1, x2, y2 = rect_tuple
            crop_w = x2 - x1
            crop_h = y2 - y1
            target_w = bt["w"] * config.GRID_CELL_SIZE
            target_h = bt["h"] * config.GRID_CELL_SIZE
            try:
                cropped = _sheet.subsurface(pygame.Rect(x1, y1, crop_w, crop_h))
                cropped = _remove_dark_background(cropped)
                scaled = pygame.transform.smoothscale(cropped, (target_w, target_h))
                _cache[name] = scaled
                if config.debug:
                    print(f"[SPRITES] ✓ {name} cached at {target_w}x{target_h}")
            except ValueError as e:
                if config.debug:
                    print(f"[SPRITES] ✗ Bad rect for {name}: {e}")


def get(name: str) -> pygame.Surface | None:
    """Return a cached scaled surface for a building name, or None if unavailable."""
    return _cache.get(name)


def is_loaded() -> bool:
    """Return True if the sprite sheet has been loaded successfully."""
    return _sheet is not None