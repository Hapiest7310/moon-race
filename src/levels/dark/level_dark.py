import math
import random
import pygame
from src import config
from src.levels.level_base import Level
from src.shaders import ShaderSurface
from src.animations import StarField, ParticleSystem, ScreenShake


# ── utility ──────────────────────────────────────────────────────────────

def _generate_rock_verts(radius, count=None):
    if count is None:
        count = random.randint(9, 14)
    verts = []
    for i in range(count):
        a = 2.0 * math.pi * i / count + random.uniform(-0.15, 0.15)
        r = radius * random.uniform(0.65, 1.35)
        verts.append((math.cos(a) * r, math.sin(a) * r))
    return verts


_ASTEROID_SPECS = {
    "large":  {"radius": 44, "score": 20,  "min_vert": 10, "max_vert": 14},
    "medium": {"radius": 24, "score": 50,  "min_vert": 8,  "max_vert": 11},
    "small":  {"radius": 12, "score": 100, "min_vert": 6,  "max_vert": 9},
}


# ── Dark Side level: Asteroids ───────────────────────────────────────────

class LevelDark(Level):

    SHIP_RADIUS = 18
    SHIP_THRUST_ACCEL = 420.0
    SHIP_MAX_SPEED = 450.0
    SHIP_ROT_SPEED = 4.2
    SHIP_INVINCIBLE_SECS = 3.0

    BULLET_SPEED = 600.0
    BULLET_RADIUS = 2.5
    BULLET_LIFETIME = 1400
    BULLET_DELAY = 220

    ASTEROID_SPEED_MIN = 25
    ASTEROID_SPEED_MAX = 90

    def __init__(self, surface, minigame=False):
        super().__init__(surface)
        self._minigame_mode = minigame
        self._init_game()

    # ── initialisation ─────────────────────────────────────────────────

    def _init_game(self):
        self.score = 0
        self.lives = 3
        self.wave = 0
        self.game_over = False
        self._restart_countdown = 0
        self._minigame_finished = False
        self._countdown_timer = config.DARK_COUNTDOWN_SECONDS * 1000
        self._countdown_active = True
        self._mining_timer = config.DARK_MINING_SECONDS * 1000
        self._stars = StarField(160)

        # Shader-like layers (blended onto frame)
        self._glow_layer = ShaderSurface(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self._particle_layer = ShaderSurface(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        # Screen shake
        self._shake = ScreenShake()

        # Frame buffer for screen shake
        self._frame_buffer = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )

        # Ship
        self._ship = None
        self._bullets = []
        self._particles = ParticleSystem()
        self._flash_particles = []
        self._init_ship()

        # Asteroids
        self.asteroids = []
        self._start_wave()

        # Fonts
        self._hud_font = pygame.font.Font(None, 32)
        self._big_font = pygame.font.Font(None, 64)
        self._go_font = pygame.font.Font(None, 96)
        self._count_font = pygame.font.Font(None, 240)

        # Wave text display
        self._wave_text = ""
        self._wave_text_timer = 0

    def is_minigame_done(self):
        return self._minigame_finished

    def get_earnings(self):
        return self.score

    def _init_ship(self):
        self._ship = {
            "pos": [config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2],
            "vel": [0.0, 0.0],
            "angle": -math.pi / 2,
            "alive": True,
            "thrust": False,
            "invincible": self.SHIP_INVINCIBLE_SECS,
            "cooldown": 0,
        }

    # ── wave management ────────────────────────────────────────────────

    def _start_wave(self):
        self.wave += 1
        count = min(3 + self.wave, 18)
        for _ in range(count):
            self._spawn_asteroid()
        self._wave_text = f"Wave {self.wave}"
        self._wave_text_timer = 2000

    def _spawn_asteroid(self, pos=None, size="large", verts=None):
        spec = _ASTEROID_SPECS[size]
        if pos is None:
            for _ in range(50):
                x = random.uniform(80, config.SCREEN_WIDTH - 80)
                y = random.uniform(80, config.SCREEN_HEIGHT - 80)
                if self._ship and self._ship["alive"]:
                    if math.hypot(x - self._ship["pos"][0],
                                  y - self._ship["pos"][1]) < 250:
                        continue
                pos = [x, y]
                break
            else:
                pos = [random.uniform(0, config.SCREEN_WIDTH),
                       random.uniform(0, config.SCREEN_HEIGHT)]
        if verts is None:
            verts = _generate_rock_verts(
                spec["radius"],
                random.randint(spec["min_vert"], spec["max_vert"]),
            )
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(self.ASTEROID_SPEED_MIN, self.ASTEROID_SPEED_MAX)
        self.asteroids.append({
            "pos": list(pos),
            "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            "rot": random.uniform(0, 2 * math.pi),
            "rot_speed": random.uniform(-1.8, 1.8),
            "radius": spec["radius"],
            "size": size,
            "verts": verts,
            "score": spec["score"],
        })

    def _split_asteroid(self, a):
        new_size = {"large": "medium", "medium": "small", "small": None}[a["size"]]
        if new_size is None:
            return
        for _ in range(2):
            off_x = random.uniform(-15, 15)
            off_y = random.uniform(-15, 15)
            p = [a["pos"][0] + off_x, a["pos"][1] + off_y]
            self._spawn_asteroid(pos=p, size=new_size)

    # ── ship helpers ───────────────────────────────────────────────────

    def _wrap_entity(self, e):
        e["pos"][0] %= config.SCREEN_WIDTH
        e["pos"][1] %= config.SCREEN_HEIGHT

    def _reset_ship(self):
        self._ship["pos"] = [config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2]
        self._ship["vel"] = [0.0, 0.0]
        self._ship["angle"] = -math.pi / 2
        self._ship["alive"] = True
        self._ship["invincible"] = self.SHIP_INVINCIBLE_SECS
        self._ship["thrust"] = False
        self._ship["cooldown"] = 0

    def _get_ship_points(self):
        s = self._ship
        a = s["angle"]
        r = self.SHIP_RADIUS
        tip = (s["pos"][0] + math.cos(a) * r * 1.2,
               s["pos"][1] + math.sin(a) * r * 1.2)
        bl = (s["pos"][0] + math.cos(a + 2.3) * r,
              s["pos"][1] + math.sin(a + 2.3) * r)
        br = (s["pos"][0] + math.cos(a - 2.3) * r,
              s["pos"][1] + math.sin(a - 2.3) * r)
        return tip, bl, br

    # ── bullets ────────────────────────────────────────────────────────

    def _shoot(self):
        s = self._ship
        if not s["alive"] or s["cooldown"] > 0:
            return
        a = s["angle"]
        bx = s["pos"][0] + math.cos(a) * self.SHIP_RADIUS * 1.4
        by = s["pos"][1] + math.sin(a) * self.SHIP_RADIUS * 1.4
        self._bullets.append({
            "pos": [bx, by],
            "vel": [math.cos(a) * self.BULLET_SPEED,
                    math.sin(a) * self.BULLET_SPEED],
            "lifetime": self.BULLET_LIFETIME,
        })
        s["cooldown"] = self.BULLET_DELAY

    # ── particles / effects ────────────────────────────────────────────

    def _emit_explosion(self, pos, color, radius, count=None):
        if count is None:
            count = max(6, int(radius * 1.6))
        self._particles.burst(
            pos[0], pos[1], count, color, (30, radius * 4),
            (300, 900), (1.5, 4.5), gravity=0, drag=0.98,
            spread=3,
        )
        # Flash
        self._flash_particles.append({
            "pos": list(pos),
            "radius": radius * 1.5,
            "life": 120,
            "max_life": 120,
            "color": (255, 255, 255),
        })
        # Screen shake
        self._shake.trigger(radius * 0.25)

    # ── collision detection ────────────────────────────────────────────

    def _check_collisions(self):
        ship = self._ship
        # Bullets → asteroids
        for b in self._bullets[:]:
            bw, bh = b["pos"]
            for a in self.asteroids[:]:
                dx = bw - a["pos"][0]
                dy = bh - a["pos"][1]
                if math.hypot(dx, dy) < self.BULLET_RADIUS + a["radius"]:
                    if a in self.asteroids:
                        self.asteroids.remove(a)
                    if b in self._bullets:
                        self._bullets.remove(b)
                    self.score += a["score"]
                    self._emit_explosion(a["pos"], (200, 180, 120), a["radius"])
                    self._split_asteroid(a)
                    break

        # Ship → asteroids
        if ship["alive"] and ship["invincible"] <= 0:
            sx, sy = ship["pos"]
            for a in self.asteroids[:]:
                dx = sx - a["pos"][0]
                dy = sy - a["pos"][1]
                if math.hypot(dx, dy) < self.SHIP_RADIUS + a["radius"]:
                    self._emit_explosion(ship["pos"], (140, 200, 255),
                                         self.SHIP_RADIUS * 1.5, count=30)
                    ship["alive"] = False
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self._restart_countdown = 1500
                    break

    # ── update ─────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Minigame exit: ESC always returns to light level
            if self._minigame_mode and event.key == pygame.K_ESCAPE:
                self._minigame_finished = True
                return

            if self.game_over:
                if self._minigame_mode:
                    self._minigame_finished = True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                    self._init_game()
                return

            if event.key == pygame.K_SPACE and not self._countdown_active:
                self._shoot()

            # Cheats
            if config.cheat_coins:
                if event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                    self.lives += 1
                    if config.debug:
                        print(f"[CHEAT] lives: {self.lives}")
                elif event.key == pygame.K_x and (event.mod & pygame.KMOD_CTRL):
                    self.asteroids.clear()
                    if config.debug:
                        print("[CHEAT] asteroids cleared")

    def update(self, dt):
        dt_sec = dt / 1000.0

        # Countdown before game starts (freezes everything)
        if self._countdown_active:
            self._countdown_timer -= dt
            if self._countdown_timer <= 0:
                self._countdown_active = False
            return

        # Mining timer
        if not self.game_over:
            self._mining_timer -= dt
            if self._mining_timer <= 0:
                self._mining_timer = 0
                self.game_over = True

        # Stars drift slowly
        self._stars.update(dt)

        # Wave text timer
        if self._wave_text_timer > 0:
            self._wave_text_timer -= dt

        # Screen shake decay
        self._shake.update(dt)

        # Ship
        ship = self._ship
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if ship["alive"]:
                # Rotation
                if keys[pygame.K_LEFT]:
                    ship["angle"] -= self.SHIP_ROT_SPEED * dt_sec
                if keys[pygame.K_RIGHT]:
                    ship["angle"] += self.SHIP_ROT_SPEED * dt_sec
                # Thrust
                ship["thrust"] = bool(keys[pygame.K_UP])
                if ship["thrust"]:
                    ax = math.cos(ship["angle"]) * self.SHIP_THRUST_ACCEL * dt_sec
                    ay = math.sin(ship["angle"]) * self.SHIP_THRUST_ACCEL * dt_sec
                    ship["vel"][0] += ax
                    ship["vel"][1] += ay
                    spd = math.hypot(*ship["vel"])
                    if spd > self.SHIP_MAX_SPEED:
                        scale = self.SHIP_MAX_SPEED / spd
                        ship["vel"][0] *= scale
                        ship["vel"][1] *= scale
                    # Thrust particles
                    tx = ship["pos"][0] - math.cos(ship["angle"]) * self.SHIP_RADIUS * 0.8
                    ty = ship["pos"][1] - math.sin(ship["angle"]) * self.SHIP_RADIUS * 0.8
                    for _ in range(2):
                        spread = random.uniform(-0.4, 0.4)
                        spd = random.uniform(50, 180)
                        self._particles.add(
                            tx + random.uniform(-3, 3),
                            ty + random.uniform(-3, 3),
                            math.cos(ship["angle"] + math.pi + spread) * spd,
                            math.sin(ship["angle"] + math.pi + spread) * spd,
                            random.uniform(150, 350), 350,
                            (255, random.randint(120, 200), random.randint(20, 80)),
                            random.uniform(1.5, 3.5),
                            gravity=0, drag_x=0.98, drag_y=0.98,
                        )
                else:
                    ship["thrust"] = False
                # Movement
                ship["pos"][0] += ship["vel"][0] * dt_sec
                ship["pos"][1] += ship["vel"][1] * dt_sec
                self._wrap_entity(ship)
                # Cooldown
                if ship["cooldown"] > 0:
                    ship["cooldown"] -= dt
                # Invincibility
                if ship["invincible"] > 0:
                    ship["invincible"] -= dt_sec
            else:
                # Respawn countdown
                if self._restart_countdown > 0:
                    self._restart_countdown -= dt
                    if self._restart_countdown <= 0:
                        self._reset_ship()

        # Bullets
        for b in self._bullets[:]:
            b["pos"][0] += b["vel"][0] * dt_sec
            b["pos"][1] += b["vel"][1] * dt_sec
            b["lifetime"] -= dt
            if b["lifetime"] <= 0:
                if b in self._bullets:
                    self._bullets.remove(b)
                continue
            self._wrap_entity(b)

        # Asteroids
        for a in self.asteroids:
            a["pos"][0] += a["vel"][0] * dt_sec
            a["pos"][1] += a["vel"][1] * dt_sec
            a["rot"] += a["rot_speed"] * dt_sec
            self._wrap_entity(a)

        # Particles
        self._particles.update(dt)

        # Flash particles
        for fp in self._flash_particles[:]:
            fp["life"] -= dt
            if fp["life"] <= 0:
                self._flash_particles.remove(fp)

        # Collisions (only when ship is alive)
        if ship["alive"] and not self.game_over:
            self._check_collisions()

        # Wave check
        if not self.asteroids and ship["alive"] and not self.game_over:
            self._start_wave()

    # ── draw ───────────────────────────────────────────────────────────

    def draw(self):
        # Use frame buffer to support screen shake offset
        target = self._frame_buffer
        target.fill((4, 4, 12))

        # Stars
        self._stars.draw(target)

        # Clear shader layers
        self._glow_layer.clear()
        self._particle_layer.clear()

        # ── Asteroids ──
        for a in self.asteroids:
            c = math.cos(a["rot"])
            s = math.sin(a["rot"])
            pts = []
            for vx, vy in a["verts"]:
                rx = vx * c - vy * s
                ry = vx * s + vy * c
                pts.append((a["pos"][0] + rx, a["pos"][1] + ry))
            pygame.draw.polygon(target, (50, 50, 65), pts)
            pygame.draw.polygon(target, (160, 160, 180), pts, 2)

        # ── Bullets ──
        for b in self._bullets:
            bx, by = int(b["pos"][0]), int(b["pos"][1])
            # Bullet core
            pygame.draw.circle(target, (255, 255, 230),
                               (bx, by), max(1, int(self.BULLET_RADIUS)))
            # Bullet glow (additive blend layer)
            pygame.draw.circle(
                self._glow_layer.surface, (255, 220, 100),
                (bx, by), self.BULLET_RADIUS * 4,
            )

        # ── Ship ──
        ship = self._ship
        if self.game_over:
            pass
        elif ship["alive"]:
            tip, bl, br = self._get_ship_points()
            ship_color = (180, 200, 255)
            if ship["invincible"] > 0:
                if int(ship["invincible"] * 6) % 2 == 0:
                    ship_color = (80, 100, 180)

            # Thrust flame
            if ship["thrust"]:
                a = ship["angle"]
                r = self.SHIP_RADIUS
                fx = ship["pos"][0] - math.cos(a) * r * 1.0
                fy = ship["pos"][1] - math.sin(a) * r * 1.0
                fl = (fx + math.cos(a + 2.3) * r * 0.5,
                      fy + math.sin(a + 2.3) * r * 0.5)
                fr = (fx + math.cos(a - 2.3) * r * 0.5,
                      fy + math.sin(a - 2.3) * r * 0.5)
                fb = (fx - math.cos(a) * r * 0.6,
                      fy - math.sin(a) * r * 0.6)
                pygame.draw.polygon(target, (255, 180, 50), [fl, fr, fb])

            # Ship hull
            pygame.draw.polygon(target, ship_color, [tip, bl, br])
            pygame.draw.polygon(target, (220, 230, 255), [tip, bl, br], 2)

            # Ship glow (additive blend layer)
            pygame.draw.circle(
                self._glow_layer.surface, (80, 120, 200, 60),
                (int(ship["pos"][0]), int(ship["pos"][1])),
                self.SHIP_RADIUS * 3,
            )

            # Thrust glow
            if ship["thrust"]:
                a = ship["angle"]
                tx = ship["pos"][0] - math.cos(a) * self.SHIP_RADIUS * 1.2
                ty = ship["pos"][1] - math.sin(a) * self.SHIP_RADIUS * 1.2
                pygame.draw.circle(
                    self._glow_layer.surface, (255, 140, 40, 80),
                    (int(tx), int(ty)), self.SHIP_RADIUS,
                )

        elif self._restart_countdown > 0:
            txt = f"Respawn in {max(1, self._restart_countdown // 1000 + 1)}"
            surf = self._hud_font.render(txt, True, (180, 180, 200))
            rect = surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                          config.SCREEN_HEIGHT // 2))
            target.blit(surf, rect)

        # Glow layer (additive blend onto frame buffer)
        self._glow_layer.blit_to(target, blend=pygame.BLEND_ADD)

        # ── Particles ──
        self._particles.draw(self._particle_layer.surface)
        self._particle_layer.blit_to(target, blend=pygame.BLEND_ADD)

        # ── Flash particles (drawn directly on frame buffer) ──
        for fp in self._flash_particles:
            t = fp["life"] / fp["max_life"]
            fr = fp["radius"] * (0.3 + 0.7 * t)
            alpha = int(t * 180)
            c = (255, 255, 255, alpha)
            pygame.draw.circle(
                target, c,
                (int(fp["pos"][0]), int(fp["pos"][1])), fr,
            )

        # ── HUD ──
        score_text = self._hud_font.render(f"Score: {self.score}", True,
                                           (200, 200, 220))
        target.blit(score_text, (20, 20))

        # Timer
        remaining = max(0, self._mining_timer / 1000)
        timer_text = self._hud_font.render(
            f"Time: {int(remaining // 60):02}:{int(remaining % 60):02}", True,
            (220, 200, 100) if remaining <= 10 else (180, 180, 200),
        )
        tr = timer_text.get_rect(midtop=(config.SCREEN_WIDTH // 2, 20))
        target.blit(timer_text, tr)

        # Lives indicator (tiny ship triangles)
        for i in range(self.lives):
            lx = config.SCREEN_WIDTH - 40 - i * 28
            ly = 30
            a = -math.pi / 2
            r = 10
            tip = (lx + math.cos(a) * r, ly + math.sin(a) * r)
            bl = (lx + math.cos(a + 2.3) * r, ly + math.sin(a + 2.3) * r)
            br = (lx + math.cos(a - 2.3) * r, ly + math.sin(a - 2.3) * r)
            pygame.draw.polygon(target, (180, 200, 255), [tip, bl, br])
            pygame.draw.polygon(target, (220, 230, 255), [tip, bl, br], 1)

        # Wave text
        if self._wave_text_timer > 0:
            a = min(255, int((self._wave_text_timer / 500) * 255))
            surf = self._big_font.render(self._wave_text, True, (220, 220, 240))
            sr = surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                       config.SCREEN_HEIGHT // 2 - 40))
            target.blit(surf, sr)

        # Game over
        if self.game_over:
            go_surf = self._go_font.render("COMPLETE", True, (200, 180, 80))
            go_r = go_surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                            config.SCREEN_HEIGHT // 2 - 40))
            target.blit(go_surf, go_r)

            earned = self._hud_font.render(
                f"Coins earned: {self.score}", True, (200, 200, 220),
            )
            er = earned.get_rect(center=(config.SCREEN_WIDTH // 2,
                                          config.SCREEN_HEIGHT // 2 + 20))
            target.blit(earned, er)

            if self._minigame_mode:
                hint = self._hud_font.render(
                    "Press Enter, Space, or ESC to return", True, (150, 160, 180),
                )
            else:
                hint = self._hud_font.render(
                    "Press R, Space, or Enter to restart", True, (150, 160, 180),
                )
            hr = hint.get_rect(center=(config.SCREEN_WIDTH // 2,
                                       config.SCREEN_HEIGHT // 2 + 60))
            target.blit(hint, hr)

        # Countdown overlay (on top of everything)
        if self._countdown_active:
            secs = max(1, int(self._countdown_timer / 1000) + 1)
            count_surf = self._count_font.render(str(secs), True, (200, 210, 240))
            cr = count_surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                             config.SCREEN_HEIGHT // 2))
            target.blit(count_surf, cr)

        # --- blit frame buffer to screen with shake offset ---
        if self._shake.timer > 0:
            self.surface.blit(target, self._shake.offset)
        else:
            self.surface.blit(target, (0, 0))

    def get_debug_info(self):
        return (f"[LEVEL] LevelDark | wave={self.wave} score={self.score} "
                f"lives={self.lives} "
                f"asteroids={len(self.asteroids)} bullets={len(self._bullets)}")
