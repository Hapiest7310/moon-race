import math
import os
import random
import pygame
from src import config


_IDLE_ANIMS = ["idle_1", "idle_2", "hiss", "lick_1", "lick_2", "sleep"]


class Cat:
    def __init__(self, grid, occupied_getter):
        self.animations = {}
        self._load_animations()

        self.grid = grid
        self._get_occupied = occupied_getter

        if "idle_1" not in self.animations or not self.animations["idle_1"]:
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.fill((255, 0, 255))
            self.animations["idle_1"] = [surf]

        self.sprite_w = self.animations["idle_1"][0].get_width()
        self.sprite_h = self.animations["idle_1"][0].get_height()

        self.x = config.CAT_START_X
        self.y = -self.sprite_h
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.direction = 1
        self._was_on_ground = True

        self.current_anim = "idle_1"
        self.frame = 0
        self.frame_timer = 0
        self._idle_anim_timer = 0
        self._current_idle_anim = "idle_1"
        self._run_anim = "run_1"

    def _ai_input(self):
        move_x = self.direction
        jump = False
        return move_x, jump

    def _ai_wall_hit(self, direction):
        cs = self.grid.cell_size
        c = self._collider()

        if direction > 0:
            wall_gx = (c.right - 1) // cs
        else:
            wall_gx = c.left // cs

        foot_gy = self._grid_gy(c.bottom - 1)
        wall_top_gy = foot_gy
        for gy in range(foot_gy, self.grid.rows):
            if self._cell_solid(wall_gx, gy):
                wall_top_gy = gy
            else:
                break

        landing_gy = wall_top_gy + 1
        landing_y = config.SCREEN_HEIGHT - (landing_gy + 1) * cs
        height = self.y - landing_y

        if height > 0:
            self.vy = -math.sqrt(2 * config.CAT_GRAVITY * height)
            self.on_ground = False

    def _load_animations(self):
        base = os.path.join(os.path.dirname(__file__), "..", "..", "..", config.CAT_SPRITES_DIR)
        base = os.path.normpath(base)
        for anim_name in os.listdir(base):
            anim_dir = os.path.join(base, anim_name)
            if not os.path.isdir(anim_dir):
                continue
            files = sorted(f for f in os.listdir(anim_dir) if f.endswith(".png"))
            frames = []
            for f in files:
                img = pygame.image.load(os.path.join(anim_dir, f)).convert_alpha()
                img = pygame.transform.scale(
                    img,
                    (int(img.get_width() * config.CAT_SCALE),
                     int(img.get_height() * config.CAT_SCALE)),
                )
                frames.append(img)
            if frames:
                self.animations[anim_name] = frames

    def _collider(self):
        cw = self.sprite_w // 2
        ch = self.sprite_h // 2
        return pygame.Rect(self.x - cw // 2, self.y - ch, cw, ch)

    def _grid_gy(self, py):
        return (config.SCREEN_HEIGHT - py - 1) // self.grid.cell_size

    def _cell_solid(self, gx, gy):
        if gy < 0:
            return True
        if gy == 0:
            return True
        return (gx, gy) in self._get_occupied()

    def update(self, dt):
        dt_sec = dt / 1000.0

        fps = config.CAT_ANIM_FPS.get(self.current_anim, 4)
        self.frame_timer += dt
        frames = self.animations[self.current_anim]
        if self.frame_timer >= 1000 // fps:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % len(frames)

        if config.debug_cat_manual:
            keys = pygame.key.get_pressed()
            move_x = 0
            if keys[pygame.K_LEFT]:
                move_x -= 1
            if keys[pygame.K_RIGHT]:
                move_x += 1
            jump = keys[pygame.K_SPACE]
        else:
            move_x, jump = self._ai_input()

        if self.on_ground:
            self.vx = move_x * config.CAT_WALK_SPEED
            if jump:
                self.vy = config.CAT_JUMP_VELOCITY
                self.on_ground = False
        else:
            self.vx += move_x * config.CAT_WALK_SPEED * 0.3 * dt_sec
            self.vx *= 0.98 ** (60.0 * dt_sec)

        old_dir = self.direction if self.vx > 0 else (-1 if self.vx < 0 else 0)
        self.x += self.vx * dt_sec
        self._resolve_horizontal()

        if not config.debug_cat_manual and old_dir != 0 and self.vx == 0 and self.on_ground:
            self._ai_wall_hit(old_dir)

        self.vy += config.CAT_GRAVITY * dt_sec
        self.y += self.vy * dt_sec
        self._resolve_vertical()

        if self.vx > 1:
            self.direction = 1
        elif self.vx < -1:
            self.direction = -1

        self._pick_animation()
        self._was_on_ground = self.on_ground

    def _resolve_horizontal(self):
        cs = self.grid.cell_size
        c = self._collider()

        if c.left < 0:
            self.x = c.w // 2
            self.vx = 0
            return
        if c.right > config.SCREEN_WIDTH:
            self.x = config.SCREEN_WIDTH - c.w // 2
            self.vx = 0
            return

        gy_top = self._grid_gy(c.top)
        gy_bot = self._grid_gy(c.bottom - 1)

        if self.vx > 0:
            gx = (c.right - 1) // cs
            for gy in range(gy_bot, gy_top + 1):
                if self._cell_solid(gx, gy):
                    self.x = gx * cs - c.w // 2
                    self.vx = 0
                    return
        elif self.vx < 0:
            gx = c.left // cs
            for gy in range(gy_bot, gy_top + 1):
                if self._cell_solid(gx, gy):
                    self.x = (gx + 1) * cs + c.w // 2
                    self.vx = 0
                    return

    def _resolve_vertical(self):
        cs = self.grid.cell_size
        c = self._collider()

        if self.vy < 0:
            gy_top = self._grid_gy(c.top)
            gx1 = c.left // cs
            gx2 = (c.right - 1) // cs
            for gx in range(gx1, gx2 + 1):
                if self._cell_solid(gx, gy_top):
                    _, bot = self.grid.grid_to_pixel(gx, gy_top)
                    self.y = bot + cs + c.h
                    self.vy = 0
                    return
            return

        gy = self._grid_gy(c.bottom)
        if gy >= 0:
            gx1 = c.left // cs
            gx2 = (c.right - 1) // cs
            for gx in range(gx1, gx2 + 1):
                if self._cell_solid(gx, gy):
                    self.y = config.SCREEN_HEIGHT - (gy + 1) * cs
                    self.vy = 0
                    self.on_ground = True
                    return

        if c.bottom >= config.SCREEN_HEIGHT:
            self.y = config.SCREEN_HEIGHT - c.h
            self.vy = 0
            self.on_ground = True
            return

        self.on_ground = False

    def _pick_animation(self):
        prev = self.current_anim
        if not self.on_ground:
            self.current_anim = "jump"
        elif abs(self.vx) > 10:
            if self._run_anim not in ("run_1", "run_2"):
                self._run_anim = random.choice(["run_1", "run_2"])
            self.current_anim = self._run_anim
            self._idle_anim_timer = 0
        else:
            self._idle_anim_timer += 1
            if self._idle_anim_timer > 120:
                self._idle_anim_timer = 0
                self._current_idle_anim = random.choice(_IDLE_ANIMS)
            self.current_anim = self._current_idle_anim
        if self.current_anim != prev:
            self.frame = 0

    def get_state(self):
        return {
            "behavior": "jump" if not self.on_ground else ("run" if abs(self.vx) > 10 else "idle"),
            "anim": self.current_anim,
        }

    def draw(self, surface):
        if self.current_anim not in self.animations:
            return
        sprite = self.animations[self.current_anim][self.frame]
        if self.direction < 0:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (self.x - self.sprite_w // 2, self.y - self.sprite_h))

        if config.debug_cat_state:
            cw, ch = self.sprite_w // 2, self.sprite_h // 2
            rect = pygame.Rect(
                self.x - cw // 2,
                self.y - ch,
                cw,
                ch,
            )
            color = (0, 255, 0) if self.on_ground else (255, 100, 100)
            pygame.draw.rect(surface, color, rect, 1)
