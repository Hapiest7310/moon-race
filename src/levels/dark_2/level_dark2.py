import math
import random
import pygame
from src import config
from src.levels.level_base import Level
from src.shaders import ShaderSurface
from src.animations import StarField, ParticleSystem, ScreenShake


_MOVE_LIST = ["dash", "shoot", "explode", "attract"]


class LevelDark2(Level):

    def __init__(self, surface, minigame=False):
        super().__init__(surface)
        self._minigame_mode = minigame
        self._init_game()

    # ── initialisation ─────────────────────────────────────────────────

    def _init_game(self):
        self.score = 0
        self.game_over = False
        self._minigame_finished = False
        self._countdown_timer = config.DARK_COUNTDOWN_SECONDS * 1000
        self._countdown_active = True
        self._mining_timer = config.DARK_MINING_SECONDS * 1000
        self._elapsed_secs = 0.0

        self._stars = StarField(160)

        self._glow_layer = ShaderSurface(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self._particles = ParticleSystem()
        self._shake = ScreenShake()
        self._frame_buffer = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        )

        self._player_pos = [config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2]
        self._player_vel = [0.0, 0.0]
        self._move_counts = {"left": 1, "right": 1, "up": 1, "down": 1}
        self._blink_timer = 0

        self._enemies = []
        self._enemy_bullets = []
        self._spawn_enemy()
        self._last_collision_time = 0
        self._last_spawn_time = 0

        self._shattered = False
        self._victory_shown = False
        self._victory_timer = 0

        self._hud_font = pygame.font.Font(None, 32)
        self._big_font = pygame.font.Font(None, 64)
        self._go_font = pygame.font.Font(None, 96)
        self._count_font = pygame.font.Font(None, 240)

    def _difficulty_mult(self):
        t = self._elapsed_secs
        mult = 1.0 + t * config.DARK2_DIFFICULTY_RATE / 60.0
        return min(mult, config.DARK2_DIFFICULTY_MAX_MULTIPLIER)

    def is_minigame_done(self):
        return self._minigame_finished

    def get_earnings(self):
        return self.score

    # ── enemy spawning ─────────────────────────────────────────────────

    def _spawn_enemy(self):
        for _ in range(50):
            x = random.uniform(80, config.SCREEN_WIDTH - 80)
            y = random.uniform(80, config.SCREEN_HEIGHT - 80)
            if math.hypot(x - self._player_pos[0],
                          y - self._player_pos[1]) < 200:
                continue
            break
        else:
            x = random.uniform(0, config.SCREEN_WIDTH)
            y = random.uniform(0, config.SCREEN_HEIGHT)
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self._enemies.append({
            "pos": [x, y],
            "radius": config.DARK2_ENEMY_RADIUS,
            "color": color,
            "state": "chase",
            "move_cooldowns": {m: 0 for m in _MOVE_LIST},
            "move_timer": 0,
            "move_data": {},
        })

    # ── prediction ─────────────────────────────────────────────────────

    def _predict_player_pos(self):
        total = sum(self._move_counts.values())
        if total == 0:
            return list(self._player_pos)
        prob_right = self._move_counts["right"] / total
        prob_left = self._move_counts["left"] / total
        prob_down = self._move_counts["down"] / total
        prob_up = self._move_counts["up"] / total
        dx = 200.0 * (prob_right - prob_left)
        dy = 200.0 * (prob_down - prob_up)
        return [self._player_pos[0] + dx, self._player_pos[1] + dy]

    # ── particles / effects ────────────────────────────────────────────

    def _emit_shatter(self, enemy):
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 200)
            self._particles.add(
                enemy["pos"][0], enemy["pos"][1],
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(500, 1200), 1200,
                enemy["color"],
                random.uniform(3, 6),
                gravity=0, drag_x=0.96, drag_y=0.96,
            )
        self._particles.burst(
            enemy["pos"][0], enemy["pos"][1], 8,
            [(255, 255, 255), enemy["color"]],
            (50, 150), (300, 600), (2, 5),
            gravity=0, drag=0.95,
        )
        self._shake.trigger(8)

    def _emit_explosion_particles(self, pos, color):
        self._particles.burst(
            pos[0], pos[1], 20, [color, (255, 200, 50)],
            (80, 250), (400, 1000), (2, 6),
            gravity=0, drag=0.96,
        )
        self._shake.trigger(6)

    # ── collision ──────────────────────────────────────────────────────

    def _check_collisions(self):
        for enemy in self._enemies:
            if enemy["state"] == "chase":
                dx = self._player_pos[0] - enemy["pos"][0]
                dy = self._player_pos[1] - enemy["pos"][1]
                if math.hypot(dx, dy) < config.DARK2_PLAYER_RADIUS + enemy["radius"]:
                    self._on_player_hit()
                    return

        for b in self._enemy_bullets[:]:
            dx = self._player_pos[0] - b["pos"][0]
            dy = self._player_pos[1] - b["pos"][1]
            if math.hypot(dx, dy) < config.DARK2_PLAYER_RADIUS + config.DARK2_BULLET_RADIUS:
                self._enemy_bullets.remove(b)
                self._on_player_hit()
                return

    def _on_player_hit(self):
        self._last_collision_time = pygame.time.get_ticks()
        self._blink_timer = config.DARK2_BLINK_DURATION
        self._enemies.clear()
        self._enemy_bullets.clear()
        self._spawn_enemy()
        self._shake.trigger(4)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self._minigame_mode and event.key == pygame.K_ESCAPE:
                self._minigame_finished = True
                return
            if (self.game_over or self._victory_shown) and not self._countdown_active:
                if self._minigame_mode:
                    self._minigame_finished = True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                    self._init_game()

    # ── move execution helpers ──────────────────────────────────────────

    def _exec_dash(self, enemy):
        enemy["move_data"]["dash_target"] = list(self._player_pos)
        enemy["move_data"]["dash_timer"] = config.DARK2_MOVE_DASH_WINDUP_MS
        enemy["state"] = "dash_windup"

    def _update_dash_windup(self, enemy, dt):
        md = enemy["move_data"]
        md["dash_timer"] -= dt
        if md["dash_timer"] <= 0:
            tx, ty = md["dash_target"]
            dx = tx - enemy["pos"][0]
            dy = ty - enemy["pos"][1]
            d = max(1, math.hypot(dx, dy))
            md["dash_dir"] = [dx / d, dy / d]
            md["dash_timer"] = config.DARK2_MOVE_DASH_DURATION_MS
            enemy["state"] = "dash_moving"

    def _update_dash_moving(self, enemy, dt_sec, dt):
        md = enemy["move_data"]
        enemy["pos"][0] += md["dash_dir"][0] * config.DARK2_MOVE_DASH_SPEED * dt_sec
        enemy["pos"][1] += md["dash_dir"][1] * config.DARK2_MOVE_DASH_SPEED * dt_sec
        md["dash_timer"] -= dt
        if md["dash_timer"] <= 0:
            enemy["move_cooldowns"]["dash"] = config.DARK2_MOVE_DASH_COOLDOWN
            md.clear()
            enemy["state"] = "chase"

    def _exec_shoot(self, enemy):
        md = enemy["move_data"]
        md["shoot_timer"] = config.DARK2_MOVE_SHOOT_WINDUP_MS
        enemy["state"] = "shoot_windup"

    def _update_shoot_windup(self, enemy, dt):
        md = enemy["move_data"]
        md["shoot_timer"] -= dt
        if md["shoot_timer"] <= 0:
            dx = self._player_pos[0] - enemy["pos"][0]
            dy = self._player_pos[1] - enemy["pos"][1]
            angle = math.atan2(dy, dx)
            count = config.DARK2_MOVE_SHOOT_COUNT
            spread = config.DARK2_MOVE_SHOOT_SPREAD
            for k in range(count):
                a = angle + spread * (k - (count - 1) / 2)
                self._enemy_bullets.append({
                    "pos": list(enemy["pos"]),
                    "vel": [math.cos(a) * config.DARK2_BULLET_SPEED,
                            math.sin(a) * config.DARK2_BULLET_SPEED],
                    "lifetime": config.DARK2_BULLET_LIFETIME,
                })
            self._emit_explosion_particles(enemy["pos"], enemy["color"])
            enemy["move_cooldowns"]["shoot"] = config.DARK2_MOVE_SHOOT_COOLDOWN
            md.clear()
            enemy["state"] = "chase"

    def _exec_explode(self, enemy):
        md = enemy["move_data"]
        md["explode_blinks_left"] = config.DARK2_MOVE_EXPLODE_BLINKS
        md["explode_blink_timer"] = config.DARK2_MOVE_EXPLODE_BLINK_INTERVAL_MS
        md["explode_visible"] = True
        enemy["state"] = "explode_windup"

    def _update_explode_windup(self, enemy, dt):
        md = enemy["move_data"]
        md["explode_blink_timer"] -= dt
        if md["explode_blink_timer"] <= 0:
            md["explode_blinks_left"] -= 1
            md["explode_visible"] = not md["explode_visible"]
            md["explode_blink_timer"] = config.DARK2_MOVE_EXPLODE_BLINK_INTERVAL_MS

            if md["explode_blinks_left"] <= 0:
                count = config.DARK2_MOVE_EXPLODE_BULLET_COUNT
                for k in range(count):
                    a = 2 * math.pi * k / count
                    self._enemy_bullets.append({
                        "pos": list(enemy["pos"]),
                        "vel": [math.cos(a) * config.DARK2_BULLET_SPEED,
                                math.sin(a) * config.DARK2_BULLET_SPEED],
                        "lifetime": config.DARK2_BULLET_LIFETIME,
                    })
                self._emit_explosion_particles(enemy["pos"], enemy["color"])
                self._shake.trigger(10)
                enemy["move_cooldowns"]["explode"] = config.DARK2_MOVE_EXPLODE_COOLDOWN
                md.clear()
                enemy["state"] = "chase"

    def _exec_attract(self, enemy):
        md = enemy["move_data"]
        md["attract_partner"] = None
        for j, other in enumerate(self._enemies):
            if other is enemy:
                continue
            if other["state"] == "attract_windup" and other["move_data"].get("attract_partner") is None:
                md["attract_partner"] = j
                other["move_data"]["attract_partner"] = self._enemies.index(enemy)
                other["move_data"]["attract_target"] = list(enemy["pos"])
                md["attract_target"] = list(other["pos"])
                break
        if md["attract_partner"] is not None:
            enemy["state"] = "attract_windup"
        else:
            enemy["move_cooldowns"]["attract"] = 1000
            enemy["state"] = "chase"

    def _update_attract_windup(self, enemy, dt_sec, dt):
        md = enemy["move_data"]
        partner = self._enemies[md["attract_partner"]] if md["attract_partner"] is not None else None
        if partner is None or partner["state"] != "attract_windup":
            md.clear()
            enemy["move_cooldowns"]["attract"] = config.DARK2_MOVE_ATTRACT_COOLDOWN
            enemy["state"] = "chase"
            return

        speed = config.DARK2_MOVE_ATTRACT_SPEED
        dx = partner["pos"][0] - enemy["pos"][0]
        dy = partner["pos"][1] - enemy["pos"][1]
        d = max(1, math.hypot(dx, dy))
        move = speed * dt_sec
        if d < move * 2:
            mx, my = (enemy["pos"][0] + partner["pos"][0]) / 2, (enemy["pos"][1] + partner["pos"][1]) / 2
            self._emit_explosion_particles([mx, my], (255, 200, 100))
            self._shake.trigger(12)
            for _ in range(3):
                a = random.uniform(0, 2 * math.pi)
                spd = random.uniform(100, 300)
                self._particles.add(
                    mx, my, math.cos(a) * spd, math.sin(a) * spd,
                    random.uniform(300, 800), 800,
                    (random.randint(200, 255), random.randint(100, 200), 50),
                    random.uniform(4, 8),
                    gravity=0, drag_x=0.96, drag_y=0.96,
                )
            if partner in self._enemies:
                self._enemies.remove(partner)
            if enemy in self._enemies:
                self._enemies.remove(enemy)
        else:
            enemy["pos"][0] += move * dx / d
            enemy["pos"][1] += move * dy / d
            md["attract_target"] = list(partner["pos"])

    # ── move selection ─────────────────────────────────────────────────

    def _pick_move(self, enemy):
        available = [m for m in _MOVE_LIST if enemy["move_cooldowns"][m] <= 0]
        if not available:
            return None
        chance_map = {
            "dash": config.DARK2_MOVE_DASH_CHANCE,
            "shoot": config.DARK2_MOVE_SHOOT_CHANCE,
            "explode": config.DARK2_MOVE_EXPLODE_CHANCE,
            "attract": config.DARK2_MOVE_ATTRACT_CHANCE,
        }
        for m in available:
            if random.random() < chance_map[m]:
                return m
        return None

    # ── update ─────────────────────────────────────────────────────────

    def update(self, dt):
        dt_sec = dt / 1000.0
        now = pygame.time.get_ticks()

        if self._countdown_active:
            self._countdown_timer -= dt
            if self._countdown_timer <= 0:
                self._countdown_active = False
                self._last_collision_time = now
            return

        if not self.game_over and not self._victory_shown:
            self._mining_timer -= dt
            self._elapsed_secs += dt_sec
            self.score += round(config.DARK2_SCORE_PER_SECOND * dt_sec)
            if self._mining_timer <= 0:
                self._mining_timer = 0
                self.game_over = True

        self._stars.update(dt)
        self._shake.update(dt)
        self._particles.update(dt)

        # Player movement
        keys = pygame.key.get_pressed()
        ax = ay = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= config.DARK2_PLAYER_ACCEL * dt_sec
            self._move_counts["left"] += 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += config.DARK2_PLAYER_ACCEL * dt_sec
            self._move_counts["right"] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ay -= config.DARK2_PLAYER_ACCEL * dt_sec
            self._move_counts["up"] += 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ay += config.DARK2_PLAYER_ACCEL * dt_sec
            self._move_counts["down"] += 1

        self._player_vel[0] = self._player_vel[0] * config.DARK2_PLAYER_FRICTION + ax
        self._player_vel[1] = self._player_vel[1] * config.DARK2_PLAYER_FRICTION + ay

        spd = math.hypot(*self._player_vel)
        if spd > config.DARK2_PLAYER_MAX_SPEED:
            scale = config.DARK2_PLAYER_MAX_SPEED / spd
            self._player_vel[0] *= scale
            self._player_vel[1] *= scale

        self._player_pos[0] += self._player_vel[0] * dt_sec
        self._player_pos[1] += self._player_vel[1] * dt_sec
        self._player_pos[0] = max(config.DARK2_PLAYER_RADIUS, min(config.SCREEN_WIDTH - config.DARK2_PLAYER_RADIUS, self._player_pos[0]))
        self._player_pos[1] = max(config.DARK2_PLAYER_RADIUS, min(config.SCREEN_HEIGHT - config.DARK2_PLAYER_RADIUS, self._player_pos[1]))

        if self._blink_timer > 0:
            self._blink_timer -= dt

        time_since_collision = now - self._last_collision_time

        # Enemy growth
        if time_since_collision > config.DARK2_ENEMY_GROW_INTERVAL and not self._shattered:
            for enemy in self._enemies:
                enemy["radius"] = min(enemy["radius"] * 1.02, config.DARK2_ENEMY_GROW_MAX_RADIUS)

        # Spawn new enemies
        if now - self._last_spawn_time > config.DARK2_ENEMY_SPAWN_INTERVAL and not self._shattered:
            self._spawn_enemy()
            self._last_spawn_time = now

        # Victory: shatter on survival
        if time_since_collision > config.DARK2_SHATTER_TIME and not self._shattered and self._enemies:
            self._shattered = True
            for enemy in self._enemies:
                self._emit_shatter(enemy)
            self._enemies.clear()
            self._enemy_bullets.clear()

        if self._shattered and not self._victory_shown:
            self._victory_timer += dt
            if self._victory_timer >= config.DARK2_VICTORY_DELAY:
                self._victory_shown = True

        # Enemy AI
        diff = self._difficulty_mult()
        predicted = self._predict_player_pos()
        for i, enemy in enumerate(self._enemies):

            # Decay cooldowns
            for m in _MOVE_LIST:
                if enemy["move_cooldowns"][m] > 0:
                    enemy["move_cooldowns"][m] = max(0, enemy["move_cooldowns"][m] - dt)

            state = enemy["state"]

            if state == "chase":
                chase_x = predicted[0] - enemy["pos"][0]
                chase_y = predicted[1] - enemy["pos"][1]
                dist = max(1, math.hypot(chase_x, chase_y))

                for j, other in enumerate(self._enemies):
                    if i != j:
                        dx = enemy["pos"][0] - other["pos"][0]
                        dy = enemy["pos"][1] - other["pos"][1]
                        d = math.hypot(dx, dy)
                        if d < enemy["radius"] + other["radius"] and d != 0:
                            enemy["pos"][0] += dx / d * 0.5
                            enemy["pos"][1] += dy / d * 0.5

                speed = config.DARK2_ENEMY_BASE_SPEED * diff
                enemy["pos"][0] += speed * dt_sec * chase_x / dist
                enemy["pos"][1] += speed * dt_sec * chase_y / dist

                move = self._pick_move(enemy)
                if move == "dash":
                    self._exec_dash(enemy)
                elif move == "shoot":
                    self._exec_shoot(enemy)
                elif move == "explode":
                    self._exec_explode(enemy)
                elif move == "attract":
                    self._exec_attract(enemy)

            elif state == "dash_windup":
                self._update_dash_windup(enemy, dt)
            elif state == "dash_moving":
                self._update_dash_moving(enemy, dt_sec, dt)
            elif state == "shoot_windup":
                self._update_shoot_windup(enemy, dt)
            elif state == "explode_windup":
                self._update_explode_windup(enemy, dt)
            elif state == "attract_windup":
                self._update_attract_windup(enemy, dt_sec, dt)

        # Bullets
        for b in self._enemy_bullets[:]:
            b["pos"][0] += b["vel"][0] * dt_sec
            b["pos"][1] += b["vel"][1] * dt_sec
            b["lifetime"] -= dt
            if b["lifetime"] <= 0:
                self._enemy_bullets.remove(b)
                continue
            if not (0 <= b["pos"][0] <= config.SCREEN_WIDTH and 0 <= b["pos"][1] <= config.SCREEN_HEIGHT):
                self._enemy_bullets.remove(b)

        # Collisions
        if not self.game_over and not self._shattered:
            self._check_collisions()

    # ── draw ───────────────────────────────────────────────────────────

    def draw(self):
        target = self._frame_buffer
        target.fill((4, 4, 12))
        self._stars.draw(target)

        self._glow_layer.clear()

        # Enemy bullets
        for b in self._enemy_bullets:
            bx, by = int(b["pos"][0]), int(b["pos"][1])
            pygame.draw.circle(target, (255, 100, 100), (bx, by), config.DARK2_BULLET_RADIUS)
            pygame.draw.circle(
                self._glow_layer.surface, (255, 50, 50, 80),
                (bx, by), config.DARK2_BULLET_RADIUS * 4,
            )

        # Enemies
        for enemy in self._enemies:
            pos = (int(enemy["pos"][0]), int(enemy["pos"][1]))
            r = int(enemy["radius"])

            visible = True
            if enemy["state"] == "explode_windup" and not enemy["move_data"].get("explode_visible", True):
                visible = False

            if visible:
                pygame.draw.circle(target, enemy["color"], pos, r)
                pygame.draw.circle(target, (255, 255, 255), pos, r, 1)
                pygame.draw.circle(
                    self._glow_layer.surface, enemy["color"] + (60,),
                    pos, r * 3,
                )

            # Dash windup indicator
            if enemy["state"] == "dash_windup":
                md = enemy["move_data"]
                target_x, target_y = int(md["dash_target"][0]), int(md["dash_target"][1])
                alpha = int(155 + 100 * math.sin(now_ms() / 100))
                pygame.draw.line(target, (*enemy["color"], alpha), pos, (target_x, target_y), 3)
                pygame.draw.circle(target, (255, 50, 50, alpha), (target_x, target_y), 8, 2)
                pygame.draw.circle(target, (255, 50, 50), pos, int(r * 2), 1)

            # Shoot windup indicator
            if enemy["state"] == "shoot_windup":
                pygame.draw.circle(target, (255, 200, 50), pos, int(r * 1.5), 2)

            # Explode windup indicator
            if enemy["state"] == "explode_windup":
                alpha = 200 if visible else 60
                pygame.draw.circle(target, (255, 100, 0, alpha), pos, int(r * 2.5), 2)
                pygame.draw.circle(target, (255, 50, 0, alpha), pos, int(r * 3.5), 1)

            # Attract windup indicator
            if enemy["state"] == "attract_windup":
                md = enemy["move_data"]
                if "attract_target" in md:
                    tx, ty = int(md["attract_target"][0]), int(md["attract_target"][1])
                    alpha = int(155 + 100 * math.sin(now_ms() / 150))
                    pygame.draw.line(target, (255, 200, 100, alpha), pos, (tx, ty), 2)

        self._particles.draw(self._glow_layer.surface, alpha_scale=200)

        # Player
        if not self._shattered:
            visible = True
            if self._blink_timer > 0 and (int(self._blink_timer / 100) % 2 == 0):
                visible = False
            if visible:
                ppos = (int(self._player_pos[0]), int(self._player_pos[1]))
                pygame.draw.circle(target, (30, 144, 255), ppos, config.DARK2_PLAYER_RADIUS - 2)
                pygame.draw.circle(target, (100, 180, 255), ppos, config.DARK2_PLAYER_RADIUS - 2, 2)
                pygame.draw.circle(
                    self._glow_layer.surface, (30, 144, 255, 40),
                    ppos, config.DARK2_PLAYER_RADIUS * 3,
                )

        self._glow_layer.blit_to(target, blend=pygame.BLEND_ADD)

        # HUD
        score_text = self._hud_font.render(f"Score: {int(self.score)}", True, (200, 200, 220))
        target.blit(score_text, (20, 20))

        remaining = max(0, self._mining_timer / 1000)
        timer_text = self._hud_font.render(
            f"Time: {int(remaining // 60):02}:{int(remaining % 60):02}", True,
            (220, 200, 100) if remaining <= 10 else (180, 180, 200),
        )
        tr = timer_text.get_rect(midtop=(config.SCREEN_WIDTH // 2, 20))
        target.blit(timer_text, tr)

        # Victory
        if self._victory_shown:
            go_surf = self._go_font.render("VICTORY!", True, (255, 215, 0))
            go_r = go_surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                            config.SCREEN_HEIGHT // 2 - 40))
            target.blit(go_surf, go_r)

            earned = self._hud_font.render(
                f"Coins earned: {int(self.score)}", True, (200, 200, 220),
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

        if self.game_over and not self._victory_shown:
            go_surf = self._go_font.render("TIME'S UP", True, (200, 180, 80))
            go_r = go_surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                            config.SCREEN_HEIGHT // 2 - 40))
            target.blit(go_surf, go_r)

            earned = self._hud_font.render(
                f"Coins earned: {int(self.score)}", True, (200, 200, 220),
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

        if self._countdown_active:
            secs = max(1, int(self._countdown_timer / 1000) + 1)
            count_surf = self._count_font.render(str(secs), True, (200, 210, 240))
            cr = count_surf.get_rect(center=(config.SCREEN_WIDTH // 2,
                                             config.SCREEN_HEIGHT // 2))
            target.blit(count_surf, cr)

        if self._shake.timer > 0:
            self.surface.blit(target, self._shake.offset)
        else:
            self.surface.blit(target, (0, 0))

    def get_debug_info(self):
        return (f"[LEVEL] LevelDark2 | score={int(self.score)} "
                f"enemies={len(self._enemies)} "
                f"diff={self._difficulty_mult():.2f}")


def now_ms():
    return pygame.time.get_ticks()
