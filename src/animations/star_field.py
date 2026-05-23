import math
import random
import pygame
from src import config


class StarField:
    """Drifting star background with optional twinkle effect.

    Two modes:
      - simple: stars drift at a uniform speed, drawn as white circles
        with varying brightness (used by Dark Side).
      - twinkle: stars drift at individual speeds with sinusoidal alpha
        blinking, drawn on an overlay surface (used by Light Side).
    """

    def __init__(self, count, twinkle=False):
        self.twinkle = twinkle
        self._stars = []
        self._time = 0.0
        self._init(count)

    def _init(self, count):
        for _ in range(count):
            if self.twinkle:
                self._stars.append({
                    "x": random.uniform(0, config.SCREEN_WIDTH),
                    "y": random.uniform(0, config.SCREEN_HEIGHT),
                    "size": random.uniform(1, 3),
                    "phase": random.uniform(0, 6.2832),
                    "speed": random.uniform(2, 6),
                    "base_alpha": random.randint(80, 200),
                    "blink_speed": random.uniform(0.5, 2),
                })
            else:
                s = random.uniform(0.4, 2.2)
                if s < 0.8:
                    b = random.randint(60, 130)
                elif s < 1.5:
                    b = random.randint(100, 180)
                else:
                    b = random.randint(150, 230)
                self._stars.append({
                    "x": random.uniform(0, config.SCREEN_WIDTH),
                    "y": random.uniform(0, config.SCREEN_HEIGHT),
                    "size": s,
                    "brightness": b,
                })

    def update(self, dt):
        dt_sec = dt / 1000.0
        self._time += dt_sec
        if self.twinkle:
            for s in self._stars:
                s["x"] += s["speed"] * dt_sec
                if s["x"] > config.SCREEN_WIDTH:
                    s["x"] -= config.SCREEN_WIDTH
        else:
            for s in self._stars:
                s["x"] -= 8 * dt_sec
                if s["x"] < -4:
                    s["x"] += config.SCREEN_WIDTH + 8
                    s["y"] = random.uniform(0, config.SCREEN_HEIGHT)

    def draw(self, surface):
        if self.twinkle:
            for s in self._stars:
                blink = math.sin(self._time * s["blink_speed"] + s["phase"])
                alpha = int(s["base_alpha"] + 55 * blink)
                alpha = max(0, min(255, alpha))
                r = max(1, int(s["size"]))
                pygame.draw.circle(
                    surface, (255, 255, 255, alpha),
                    (int(s["x"]), int(s["y"])), r,
                )
        else:
            for s in self._stars:
                r = max(1, int(s["size"]))
                b = int(s["brightness"])
                pygame.draw.circle(
                    surface, (b, b, b),
                    (int(s["x"]), int(s["y"])), r,
                )
