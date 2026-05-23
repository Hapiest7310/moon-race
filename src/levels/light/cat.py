import os
import random
import pygame
from src import config


ANIM_BEHAVIOR = {
    "idle_1": "idle", "idle_2": "idle",
    "run_1": "run", "run_2": "run",
    "jump": "jump",
    "hiss": "idle", "lick_1": "idle", "lick_2": "idle",
    "punch": "idle", "sleep": "idle",
}


class Cat:
    def __init__(self, grid, buildings_getter):
        self.animations = {}
        self._load_animations()

        self.grid = grid
        self._get_buildings = buildings_getter

        self.x = config.CAT_START_X
        self.y = config.SCREEN_HEIGHT - self.animations["idle_1"][0].get_height()
        self.direction = 1

        self.current_anim = "idle_1"
        self.frame = 0
        self.frame_timer = 0

        self.behavior = "idle"
        self.state_timer = 0
        self.state_duration = random.randint(*config.CAT_IDLE_DURATION_RANGE)

        self.jump_phase = 0
        self.jump_start_y = self.y
        # climb plan: None or dict with keys: target_gx, target_gy, phase
        self.climb_plan = None

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

    def update(self, dt):
        fps = config.CAT_ANIM_FPS.get(self.current_anim, 4)
        self.frame_timer += dt
        if self.frame_timer >= 1000 // fps:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % len(self.animations[self.current_anim])

        self.state_timer += dt

        if self.behavior == "idle":
            self._update_idle(dt)
        elif self.behavior == "run":
            self._update_run(dt)
        elif self.behavior == "jump":
            self._update_jump(dt)
        elif self.behavior == "climb":
            self._update_climb(dt)

    def _update_idle(self, dt):
        if self.state_timer >= self.state_duration:
            self._pick_next_state()

    def _update_run(self, dt):
        self.x += self.direction * config.CAT_RUN_SPEED * (dt / 16.67)
        sprite_w = self.animations[self.current_anim][0].get_width()
        if self.x + sprite_w > config.SCREEN_WIDTH:
            self.x = config.SCREEN_WIDTH - sprite_w
            self.direction = -1
        elif self.x < 0:
            self.x = 0
            self.direction = 1
        if self.state_timer >= self.state_duration:
            self._pick_next_state()

    def _update_jump(self, dt):
        self.jump_phase += 1
        progress = self.jump_phase / config.CAT_JUMP_FRAMES
        offset = int(config.CAT_JUMP_HEIGHT * 2 * (0.5 - abs(0.5 - progress)))
        self.y = self.jump_start_y - offset
        self.x += self.direction * config.CAT_RUN_SPEED * 0.5 * (dt / 16.67)
        sprite_w = self.animations[self.current_anim][0].get_width()
        if self.x + sprite_w > config.SCREEN_WIDTH:
            self.x = config.SCREEN_WIDTH - sprite_w
        elif self.x < 0:
            self.x = 0
        if self.jump_phase >= config.CAT_JUMP_FRAMES:
            self.y = self.jump_start_y
            self.jump_phase = 0
            self._pick_next_state()

    def _update_climb(self, dt):
        # climb consists of two phases: horizontal align to target_gx, then vertical straight-up jump
        if not self.climb_plan:
            # no plan, fallback
            self._pick_next_state()
            return
        phase = self.climb_plan.get("phase")
        target_gx = self.climb_plan.get("target_gx")
        target_gy = self.climb_plan.get("target_gy")
        cs = self.grid.cell_size

        # compute current feet grid x
        sprite_w = self.animations[self.current_anim][0].get_width()
        feet_x = self.x + sprite_w // 2
        cur_gx, cur_gy = self.grid.pixel_to_grid(feet_x, self.y + self.animations[self.current_anim][0].get_height())

        if phase == "horiz":
            # move toward target_gx in pixel space
            target_px = target_gx * cs + (cs - sprite_w) // 2
            dir = 1 if target_px > self.x else -1
            self.direction = dir
            step = config.CAT_GRID_SPEED * (dt / 1000.0)
            if abs(target_px - self.x) <= step:
                self.x = target_px
                # switch to vertical phase
                self.climb_plan["phase"] = "vert"
                # prepare jump parameters
                self.jump_start_y = self.y
                self.jump_phase = 0
                # compute rows to climb
                self.climb_plan["rows"] = max(0, target_gy - cur_gy)
                # compute vertical jump frames based on rows
                rows = self.climb_plan["rows"]
                self.climb_plan["frames"] = max(6, int(rows * (config.CAT_CLIMB_MS_PER_ROW / (1000.0 / config.CAT_ANIM_FPS.get("jump", 8)))))
            else:
                self.x += dir * step

        elif phase == "vert":
            # perform straight-up jump to target_gy; no diagonal
            rows = self.climb_plan.get("rows", 0)
            frames = self.climb_plan.get("frames", config.CAT_JUMP_FRAMES)
            self.jump_phase += 1
            progress = min(1.0, self.jump_phase / max(1, frames))
            # compute peak: rows * cell_size plus base height with overshoot
            base = rows * cs
            overshoot = int(base * config.CAT_JUMP_OVERSHOOT_FACTOR)
            peak = base + overshoot + config.CAT_JUMP_HEIGHT
            # parabolic motion
            offset = int(peak * 2 * (0.5 - abs(0.5 - progress)))
            self.y = self.jump_start_y - offset
            if self.jump_phase >= frames:
                # land on target surface: compute target pixel y (top of target cell)
                target_px_y = config.SCREEN_HEIGHT - (target_gy + 1) * cs - self.animations[self.current_anim][0].get_height() + cs
                # Simplify: align feet to top of target cell
                self.y = config.SCREEN_HEIGHT - (target_gy + 1) * cs - (self.animations[self.current_anim][0].get_height() - cs)
                # done climbing
                self.climb_plan = None
                self._pick_next_state()
                return

        else:
            # unknown phase
            self.climb_plan = None
            self._pick_next_state()

    def _pick_next_state(self):
        weights = config.CAT_TRANSITIONS[self.behavior]
        next_state = random.choices(
            list(weights.keys()), weights=list(weights.values())
        )[0]

        if next_state == "idle":
            anim = random.choice(["idle_1", "idle_2", "hiss", "lick_1", "lick_2", "sleep"])
            if anim == "hiss":
                self.state_duration = random.randint(*config.CAT_HISS_DURATION_RANGE)
            elif anim == "sleep":
                self.state_duration = random.randint(3000, 6000)
            else:
                self.state_duration = random.randint(*config.CAT_IDLE_DURATION_RANGE)
        elif next_state == "run":
            anim = random.choice(["run_1", "run_2"])
            self.state_duration = random.randint(*config.CAT_RUN_DURATION_RANGE)
        elif next_state == "jump":
            anim = "jump"
            self.jump_phase = 0
            self.jump_start_y = self.y
            self.state_duration = 999999
        elif next_state == "climb":
            # prepare climb plan
            anim = "run_1"
            self._start_climb()
        else:
            anim = "idle_1"
            self.state_duration = random.randint(*config.CAT_IDLE_DURATION_RANGE)

        self.behavior = next_state
        self.current_anim = anim
        self.frame = 0
        self.frame_timer = 0
        self.state_timer = 0

    def _start_climb(self):
        buildings = self._get_buildings()
        if not buildings:
            return
        b = random.choice(buildings)
        # choose a cell on top of the building
        gx0 = b.get("gx", 0)
        w = b.get("width", b.get("w", 1))
        gy_top = b.get("gy", 0) + b.get("height", b.get("h", 1)) - 1
        target_gx = random.randint(gx0, gx0 + max(0, w - 1))
        self.climb_plan = {"target_gx": target_gx, "target_gy": gy_top, "phase": "horiz"}
        # ensure cat uses a running animation during approach
        self.current_anim = "run_1"
        self.frame = 0
        self.frame_timer = 0
        self.state_timer = 0

    # public API to trigger climb externally
    def start_climb(self):
        self.behavior = "climb"
        self._start_climb()

    def start_climb_to(self, target_gx, target_gy):
        # set a manual climb plan to a specific target cell
        self.behavior = "climb"
        self.climb_plan = {"target_gx": int(target_gx), "target_gy": int(target_gy), "phase": "horiz"}
        self.current_anim = "run_1"
        self.frame = 0
        self.frame_timer = 0
        self.state_timer = 0

    def get_debug_plan(self):
        return self.climb_plan

    def get_state(self):
        return {"behavior": self.behavior, "anim": self.current_anim}

    def draw(self, surface):
        if self.current_anim not in self.animations:
            return
        sprite = self.animations[self.current_anim][self.frame]
        if self.direction < 0:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (self.x, self.y))
