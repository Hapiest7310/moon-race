import math
import random
import pygame


class ParticleSystem:
    """Reusable particle emitter / updater / renderer.

    Each particle stores its own gravity and per-axis drag so a single
    system can hold mixed particle types (explosions, thrust, debris…).
    """

    def __init__(self):
        self.particles = []

    def add(self, x, y, vx, vy, life, max_life, color, size,
            gravity=0.0, drag_x=1.0, drag_y=1.0):
        self.particles.append({
            "x": x, "y": y,
            "vx": vx, "vy": vy,
            "life": life, "max_life": max_life,
            "color": color, "size": size,
            "gravity": gravity, "drag_x": drag_x, "drag_y": drag_y,
        })

    def burst(self, cx, cy, count, color, speed, lifetime, size_range,
              angle_span=6.2832, gravity=0.0, drag=1.0, spread=0,
              upward_bias=0):
        """Emit *count* particles in an arc (default full circle)."""
        if isinstance(speed, (tuple, list)):
            speed_min, speed_max = speed
        else:
            speed_min = speed_max = speed
        if isinstance(lifetime, (tuple, list)):
            life_min, life_max = lifetime
        else:
            life_min = life_max = lifetime
        colors = color if isinstance(color, (tuple, list)) and isinstance(color[0], (tuple, list)) else [color]
        for _ in range(count):
            a = random.uniform(0, angle_span)
            spd = random.uniform(speed_min, speed_max)
            self.add(
                cx + random.uniform(-spread, spread),
                cy + random.uniform(-spread, spread),
                math.cos(a) * spd,
                math.sin(a) * spd - upward_bias,
                random.uniform(life_min, life_max),
                life_max,
                random.choice(colors),
                random.uniform(size_range[0], size_range[1]),
                gravity, drag, drag,
            )

    def update(self, dt):
        dt_sec = dt / 1000.0
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt_sec
            p["y"] += p["vy"] * dt_sec
            p["vy"] += p["gravity"] * dt_sec
            p["vx"] *= p["drag_x"]
            p["vy"] *= p["drag_y"]
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surface, alpha_scale=200):
        for p in self.particles:
            t = p["life"] / p["max_life"]
            if t <= 0:
                continue
            alpha = int(max(0, t * alpha_scale))
            r = max(1, int(p["size"] * (0.3 + 0.7 * t)))
            c = p["color"]
            color = (min(255, c[0]), min(255, c[1]), min(255, c[2]))
            pygame.draw.circle(
                surface, color + (alpha,),
                (int(p["x"]), int(p["y"])), r,
            )

    def clear(self):
        self.particles.clear()

    @property
    def alive(self):
        return len(self.particles) > 0
