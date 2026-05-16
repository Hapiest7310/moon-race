import json
import math
import os
import random
import pygame
from src import config
from src.levels.level_base import Level
from src.grid import Grid
from src.widget.building_menu import BuildingMenu


class LevelLight(Level):
    def __init__(self, surface, save_name="default"):
        super().__init__(surface)
        self._save_name = save_name
        self.grid = Grid()
        self.money = config.STARTING_MONEY
        self.buildings = []
        self._occupied_cells = set()
        self._hover_cell = None

        self.building_menu = BuildingMenu(
            pygame.Rect(0, 0, config.SCREEN_WIDTH, 70),
        )
        self.widgets = [self.building_menu]

        self._last_gx = -1
        self._last_gy = -1

        self.mode = "CONSTRUCT"

        self._hover_font = pygame.font.Font(None, 18)
        self._money_font = pygame.font.Font(None, 36)
        self._mode_font = pygame.font.Font(None, 22)
        self._valid_highlight = pygame.Surface(
            (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
        )
        self._invalid_highlight = pygame.Surface(
            (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
        )
        self._demolish_highlight = pygame.Surface(
            (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
        )
        self._valid_highlight.fill((0, 255, 0, 60))
        self._invalid_highlight.fill((255, 0, 0, 60))
        self._demolish_highlight.fill((255, 100, 100, 80))

        self._mode_rect = pygame.Rect(10, 74, 130, 28)

        self._snow_overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._snow_overlay.set_alpha(51)
        self._snow_particles = []
        self._init_snow(120)

        self._star_overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._stars = []
        self._star_time = 0
        self._init_stars(200)

        self.load()

    # ── snow overlay ──────────────────────────────────────────────────

    def _init_snow(self, count):
        for _ in range(count):
            self._snow_particles.append({
                "x": random.uniform(0, config.SCREEN_WIDTH),
                "y": random.uniform(0, config.SCREEN_HEIGHT),
                "size": random.uniform(3, 8),
                "speed": random.uniform(15, 40),
                "drift": random.uniform(-12, 12),
            })

    def _update_snow(self, dt):
        dt_sec = dt / 1000.0
        for p in self._snow_particles:
            p["y"] -= p["speed"] * dt_sec
            p["x"] += p["drift"] * dt_sec
            p["size"] -= 0.3 * dt_sec
            if p["x"] < 0:
                p["x"] += config.SCREEN_WIDTH
            elif p["x"] > config.SCREEN_WIDTH:
                p["x"] -= config.SCREEN_WIDTH
            if p["size"] <= 1:
                p["x"] = random.uniform(0, config.SCREEN_WIDTH)
                p["y"] = config.SCREEN_HEIGHT + random.uniform(0, 10)
                p["size"] = random.uniform(3, 8)
                p["speed"] = random.uniform(15, 40)
                p["drift"] = random.uniform(-12, 12)

    def _draw_snow(self):
        self._snow_overlay.fill((0, 0, 0, 0))
        for p in self._snow_particles:
            r = max(1, int(p["size"]))
            pygame.draw.circle(
                self._snow_overlay, (255, 255, 255),
                (int(p["x"]), int(p["y"])), r,
            )
        self.surface.blit(self._snow_overlay, (0, 0))

    # ── star background ───────────────────────────────────────────────

    def _init_stars(self, count):
        for _ in range(count):
            self._stars.append({
                "x": random.uniform(0, config.SCREEN_WIDTH),
                "y": random.uniform(0, config.SCREEN_HEIGHT),
                "size": random.uniform(1, 3),
                "phase": random.uniform(0, 2 * math.pi),
                "speed": random.uniform(2, 6),
                "base_alpha": random.randint(80, 200),
                "blink_speed": random.uniform(0.5, 2),
            })

    def _update_stars(self, dt):
        dt_sec = dt / 1000.0
        self._star_time += dt_sec
        for s in self._stars:
            s["x"] += s["speed"] * dt_sec
            if s["x"] > config.SCREEN_WIDTH:
                s["x"] -= config.SCREEN_WIDTH

    def _draw_stars(self):
        self._star_overlay.fill((0, 0, 0, 0))
        for s in self._stars:
            blink = math.sin(self._star_time * s["blink_speed"] + s["phase"])
            alpha = int(s["base_alpha"] + 55 * blink)
            alpha = max(0, min(255, alpha))
            color = (255, 255, 255, alpha)
            r = max(1, int(s["size"]))
            pygame.draw.circle(
                self._star_overlay, color,
                (int(s["x"]), int(s["y"])), r,
            )
        self.surface.blit(self._star_overlay, (0, 0))

    # ── support check ─────────────────────────────────────────────────

    def _is_supported(self, gx, gy, w, h):
        if gy == 0:
            return True
        for dx in range(w):
            below = (gx + dx, gy - 1)
            if below in self._occupied_cells:
                return True
        return False

    def _can_place(self, gx, gy, w, h):
        bt = self.building_menu.get_selected_building()
        if self.money < bt["cost"]:
            return False
        for dy in range(h):
            for dx in range(w):
                cx, cy = gx + dx, gy + dy
                if not self.grid.is_in_bounds(cx, cy):
                    return False
                if (cx, cy) in self._occupied_cells:
                    return False
        return self._is_supported(gx, gy, w, h)

    # ── demolition checks ─────────────────────────────────────────────

    def _get_building_at(self, gx, gy):
        for b in self.buildings:
            if (b["gx"] <= gx < b["gx"] + b["width"] and
                b["gy"] <= gy < b["gy"] + b["height"]):
                return b
        return None

    def _has_building_on_top(self, building):
        top_y = building["gy"] + building["height"]
        for other in self.buildings:
            if other is building:
                continue
            if other["gy"] != top_y:
                continue
            if (other["gx"] < building["gx"] + building["width"] and
                other["gx"] + other["width"] > building["gx"]):
                return True
        return False

    # ── events ────────────────────────────────────────────────────────

    def handle_event(self, event):
        if config.cheat_coins and event.type == pygame.KEYDOWN:
            shift = event.mod & pygame.KMOD_SHIFT
            if event.key == pygame.K_MINUS:
                amount = 100 if shift else 10
                self.money -= amount
                if config.debug:
                    print(f"[CHEAT] coins: {self.money}")
            elif event.key == pygame.K_EQUALS:
                amount = 100 if shift else 10
                self.money += amount
                if config.debug:
                    print(f"[CHEAT] coins: {self.money}")
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._mode_rect.collidepoint(event.pos):
                self.mode = "DEMOLISH" if self.mode == "CONSTRUCT" else "CONSTRUCT"
                if config.debug:
                    print(f"[MODE] {self.mode}")
                return
            for widget in self.widgets:
                if widget.handle_event(event):
                    return
            if self._is_over_widget(event.pos):
                return
            gx, gy = self.grid.pixel_to_grid(*event.pos)
            if not self.grid.is_in_bounds(gx, gy):
                return
            if self.mode == "DEMOLISH":
                self._demolish(gx, gy)
            else:
                bt = self.building_menu.get_selected_building()
                if not self._can_place(gx, gy, bt["w"], bt["h"]):
                    return
                self._place_building(gx, gy, bt)

    def _is_over_widget(self, pos):
        for w in self.widgets:
            if w.visible and w.rect.collidepoint(pos):
                return True
        return False

    def _place_building(self, gx, gy, bt):
        cells = []
        for dy in range(bt["h"]):
            for dx in range(bt["w"]):
                cells.append((gx + dx, gy + dy))
        self.buildings.append({
            "type": bt["name"],
            "gx": gx,
            "gy": gy,
            "width": bt["w"],
            "height": bt["h"],
            "color": bt["color"],
            "cost": bt["cost"],
        })
        self._occupied_cells.update(cells)
        self.money -= bt["cost"]
        if config.debug:
            print(f"[BUILD] placed {bt['name']} at ({gx},{gy}) money={self.money}")
        self.save()

    def _demolish(self, gx, gy):
        building = self._get_building_at(gx, gy)
        if not building:
            return
        if self._has_building_on_top(building):
            if config.debug:
                print(f"[DEMOLISH] blocked — building on top of {building['type']} at ({building['gx']},{building['gy']})")
            return
        for dy in range(building["height"]):
            for dx in range(building["width"]):
                self._occupied_cells.discard((building["gx"] + dx, building["gy"] + dy))
        refund = building["cost"] // 2
        self.money += refund
        self.buildings.remove(building)
        if config.debug:
            print(f"[DEMOLISH] removed {building['type']} at ({building['gx']},{building['gy']}) refund={refund} money={self.money}")
        self.save()

    # ── update ────────────────────────────────────────────────────────

    def update(self, dt):
        self._update_snow(dt)
        self._update_stars(dt)
        self.building_menu.money = self.money
        self.building_menu.visible = self.mode == "CONSTRUCT"
        px, py = pygame.mouse.get_pos()
        if self._is_over_widget((px, py)) or self._mode_rect.collidepoint((px, py)):
            self._hover_cell = None
        else:
            gx, gy = self.grid.pixel_to_grid(px, py)
            if self.grid.is_in_bounds(gx, gy):
                self._hover_cell = (gx, gy)
            else:
                self._hover_cell = None

    # ── draw ──────────────────────────────────────────────────────────

    def draw(self):
        self.surface.fill((0, 0, 0))
        self._draw_stars()
        self._draw_buildings()
        self._draw_snow()
        self.grid.draw(self.surface)
        self._draw_hover()
        for widget in self.widgets:
            widget.draw(self.surface)
        self._draw_mode_toggle()
        self._draw_money()

    def _draw_buildings(self):
        for b in self.buildings:
            for dy in range(b["height"]):
                for dx in range(b["width"]):
                    px, py = self.grid.grid_to_pixel(b["gx"] + dx, b["gy"] + dy)
                    rect = pygame.Rect(px, py, self.grid.cell_size, self.grid.cell_size)
                    pygame.draw.rect(self.surface, b["color"], rect)

    def _draw_hover(self):
        if not self._hover_cell:
            return
        gx, gy = self._hover_cell
        if self.mode == "DEMOLISH":
            building = self._get_building_at(gx, gy)
            if building:
                for dy in range(building["height"]):
                    for dx in range(building["width"]):
                        cx, cy = building["gx"] + dx, building["gy"] + dy
                        px, py = self.grid.grid_to_pixel(cx, cy)
                        rect = pygame.Rect(px, py, self.grid.cell_size, self.grid.cell_size)
                        self.surface.blit(self._demolish_highlight, rect)
                if config.debug and config.debug_hover:
                    label = self._hover_font.render(
                        f"DEMO {building['type']}", True, (255, 150, 150)
                    )
                    px, py = self.grid.grid_to_pixel(gx, gy)
                    self.surface.blit(label, (px + 2, py + 2))
            return
        bt = self.building_menu.get_selected_building()
        w, h = bt["w"], bt["h"]
        can_place = self._can_place(gx, gy, w, h)
        highlight = self._valid_highlight if can_place else self._invalid_highlight
        for dy in range(h):
            for dx in range(w):
                cx, cy = gx + dx, gy + dy
                if self.grid.is_in_bounds(cx, cy):
                    px, py = self.grid.grid_to_pixel(cx, cy)
                    rect = pygame.Rect(px, py, self.grid.cell_size, self.grid.cell_size)
                    self.surface.blit(highlight, rect)
        if config.debug and config.debug_hover:
            label = self._hover_font.render(
                f"({gx},{gy}) {'OK' if can_place else 'NO'}", True, (255, 255, 200)
            )
            px, py = self.grid.grid_to_pixel(gx, gy)
            self.surface.blit(label, (px + 2, py + 2))

    def _draw_mode_toggle(self):
        label = "Build" if self.mode == "CONSTRUCT" else "Demolish"
        bg = (50, 120, 70) if self.mode == "CONSTRUCT" else (160, 60, 60)
        pygame.draw.rect(self.surface, bg, self._mode_rect)
        pygame.draw.rect(self.surface, (180, 180, 180), self._mode_rect, 1)
        text = self._mode_font.render(label, True, (255, 255, 255))
        tx = self._mode_rect.x + (self._mode_rect.w - text.get_width()) // 2
        ty = self._mode_rect.y + (self._mode_rect.h - text.get_height()) // 2
        self.surface.blit(text, (tx, ty))

    def _draw_money(self):
        text = self._money_font.render(f"$ {self.money}", True, (255, 220, 50))
        self.surface.blit(text, (config.SCREEN_WIDTH - text.get_width() - 20, 20))

    # ── save / load ───────────────────────────────────────────────────

    def save(self):
        os.makedirs(config.SAVE_DIR, exist_ok=True)
        path = os.path.join(config.SAVE_DIR, f"{self._save_name}.json")
        data = {
            "money": self.money,
            "buildings": [
                {"type": b["type"], "gx": b["gx"], "gy": b["gy"]}
                for b in self.buildings
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        if config.debug:
            print(f"[SAVE] saved to {path}")

    def load(self):
        path = os.path.join(config.SAVE_DIR, f"{self._save_name}.json")
        if not os.path.isfile(path):
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self.money = data.get("money", config.STARTING_MONEY)
            bt_map = {bt["name"]: bt for bt in config.BUILDING_TYPES}
            for entry in data.get("buildings", []):
                bt = bt_map.get(entry["type"])
                if not bt:
                    continue
                self.buildings.append({
                    "type": bt["name"],
                    "gx": entry["gx"],
                    "gy": entry["gy"],
                    "width": bt["w"],
                    "height": bt["h"],
                    "color": bt["color"],
                    "cost": bt["cost"],
                })
                for dy in range(bt["h"]):
                    for dx in range(bt["w"]):
                        self._occupied_cells.add((entry["gx"] + dx, entry["gy"] + dy))
            if config.debug:
                print(f"[LOAD] loaded {len(self.buildings)} buildings, money={self.money}")
        except (json.JSONDecodeError, KeyError) as e:
            if config.debug:
                print(f"[LOAD] failed: {e}")

    def get_debug_info(self):
        return f"[LEVEL] LevelLight | buildings={len(self.buildings)} money={self.money}"
