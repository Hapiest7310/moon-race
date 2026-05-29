import json
import math
import os
import random
import pygame
from src import config
from src.levels.level_base import Level
from src.levels.light.grid import Grid
from src.ui.widget.building_menu import BuildingMenu
from src.shaders import ShaderSurface
from src.levels.light.cat import Cat
import src.animations.building_sprites as building_sprites


class LevelLight(Level):
    def __init__(self, surface, save_name="default"):
        super().__init__(surface)
        building_sprites.load("assets/images/Buildings.png")
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
        self._mine_font = pygame.font.Font(None, 20)
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
        self._mine_rect = pygame.Rect(config.SCREEN_WIDTH - 180, 74, 170, 28)
        self._alien_rect = pygame.Rect(config.SCREEN_WIDTH - 180, 108, 170, 28)

        self._snow_overlay = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._snow_overlay.set_alpha(51)
        self._snow_particles = []
        self._init_snow(120)

        self._star_overlay = ShaderSurface(
            config.SCREEN_WIDTH, config.SCREEN_HEIGHT,
        )
        self._stars = []
        self._star_time = 0
        self._init_stars(200)

        self._falling_buildings = []
        self._drop_particles = []
        self._demolish_particles = []

        self.cat = Cat(self.grid, lambda: self._occupied_cells)
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
        self._star_overlay.clear()
        for s in self._stars:
            blink = math.sin(self._star_time * s["blink_speed"] + s["phase"])
            alpha = int(s["base_alpha"] + 55 * blink)
            alpha = max(0, min(255, alpha))
            color = (255, 255, 255, alpha)
            r = max(1, int(s["size"]))
            pygame.draw.circle(
                self._star_overlay.surface, color,
                (int(s["x"]), int(s["y"])), r,
            )
        self._star_overlay.blit_to(self.surface, blend=pygame.BLEND_ADD)

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
        if event.type == pygame.KEYDOWN:
            key = event.key
            if pygame.K_1 <= key <= pygame.K_9 and self.building_menu.visible:
                num = key - pygame.K_0
                if self.building_menu.select_by_key(num):
                    if config.debug:
                        bt = self.building_menu.get_selected_building()
                        print(f"[BUILD] selected {bt['name']} (key {num})")
                    return

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
            if self._mine_rect.collidepoint(event.pos):
                config.set_mine_requested(True)
                if config.debug:
                    print("[MINE] requested dark side mining")
                return
            if self._alien_rect.collidepoint(event.pos):
                config.set_alien_requested(True)
                if config.debug:
                    print("[ALIEN] requested alien evasion")
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
                self._start_drop(gx, gy, bt)

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

    def _start_drop(self, gx, gy, bt):
        cells = [(gx + dx, gy + dy) for dy in range(bt["h"]) for dx in range(bt["w"])]
        self._occupied_cells.update(cells)
        self.money -= bt["cost"]
        self._falling_buildings.append({
            "bt": dict(bt),
            "gx": gx,
            "gy": gy,
            "cells": cells,
            "progress": 0.0,
            "duration": config.DROP_ANIMATION_MS,
        })
        if config.debug:
            print(f"[DROP] started {bt['name']} at ({gx},{gy})")

    def _complete_drop(self, fb):
        bt = fb["bt"]
        self.buildings.append({
            "type": bt["name"],
            "gx": fb["gx"],
            "gy": fb["gy"],
            "width": bt["w"],
            "height": bt["h"],
            "color": bt["color"],
            "cost": bt["cost"],
        })
        self._falling_buildings.remove(fb)
        if config.debug:
            print(f"[BUILD] landed {bt['name']} at ({fb['gx']},{fb['gy']}) money={self.money}")
        self.save()

    def _demolish(self, gx, gy):
        building = self._get_building_at(gx, gy)
        if not building:
            return
        if building.get("type") == "Ground":
            if config.debug:
                print(f"[DEMOLISH] blocked — ground tile at ({gx},{gy}) cannot be demolished")
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
        self._emit_demolish_explosion(building)
        self.save()

    # ── demolish explosion ─────────────────────────────────────────────

    def _emit_demolish_explosion(self, building):
        cs = self.grid.cell_size
        cx = (building["gx"] + building["width"] / 2) * cs
        cy = config.SCREEN_HEIGHT - (building["gy"] + building["height"] / 2) * cs
        color = building["color"]
        count = max(8, building["width"] * building["height"] * 4)
        for _ in range(count):
            a = random.uniform(0, 2 * math.pi)
            spd = random.uniform(80, 280)
            self._demolish_particles.append({
                "x": cx + random.uniform(-12, 12),
                "y": cy + random.uniform(-12, 12),
                "vx": math.cos(a) * spd,
                "vy": math.sin(a) * spd - random.uniform(20, 80),
                "life": random.uniform(250, 600),
                "max_life": 600,
                "color": random.choice([color, (255, 200, 100), (200, 200, 200)]),
                "size": random.uniform(2, 5),
            })

    # ── drop animation ────────────────────────────────────────────────

    def _compute_drop_offset(self, progress):
        t = (1 - math.exp(-4 * progress)) / (1 - math.exp(-4))
        return int(-config.SCREEN_HEIGHT * (1 - t))

    def _emit_drop_particles(self, fb, offset_y):
        bt = fb["bt"]
        cs = self.grid.cell_size
        gx, gy = fb["gx"], fb["gy"]
        w, h = bt["w"], bt["h"]
        bottom_py = config.SCREEN_HEIGHT - gy * cs + offset_y
        left_px = gx * cs
        right_px = (gx + w) * cs
        for _ in range(3):
            self._drop_particles.append({
                "x": random.uniform(left_px, right_px),
                "y": bottom_py,
                "vx": random.uniform(-60, 60),
                "vy": random.uniform(150, 350),
                "life": random.uniform(200, 450),
                "max_life": 450,
                "color": (255, random.randint(140, 220), random.randint(20, 100)),
                "size": random.uniform(2, 5),
            })

    def _update_falling_buildings(self, dt):
        for fb in self._falling_buildings[:]:
            fb["progress"] += dt / fb["duration"]
            if fb["progress"] >= 1.0:
                self._complete_drop(fb)
                continue
            offset_y = self._compute_drop_offset(fb["progress"])
            fb["_offset_y"] = offset_y
            self._emit_drop_particles(fb, offset_y)
        for p in self._drop_particles[:]:
            dt_sec = dt / 1000.0
            p["x"] += p["vx"] * dt_sec
            p["y"] += p["vy"] * dt_sec
            p["vy"] += 400 * dt_sec
            p["life"] -= dt
            if p["life"] <= 0:
                self._drop_particles.remove(p)

    def _draw_falling_buildings(self):
        for fb in self._falling_buildings:
            offset_y = fb.get("_offset_y", -config.SCREEN_HEIGHT)
            bt = fb["bt"]
            gx, gy = fb["gx"], fb["gy"]
            px, py = self.grid.grid_to_pixel(gx, gy)
            py = py - (bt["h"] - 1) * config.GRID_CELL_SIZE + offset_y
            self._draw_building(self.surface, bt, px, py)
            if fb["progress"] < 1.0:
                self._draw_thrust_flame(fb, offset_y)

    def _draw_thrust_flame(self, fb, offset_y):
        cs = self.grid.cell_size
        bt = fb["bt"]
        gx, gy = fb["gx"], fb["gy"]
        w, h = bt["w"], bt["h"]
        bottom_py = config.SCREEN_HEIGHT - gy * cs + offset_y
        left_px = gx * cs
        right_px = (gx + w) * cs
        center_x = (left_px + right_px) // 2
        flicker = 0.7 + random.random() * 0.6
        flame_h = int(cs * 1.8 * flicker)
        mid_bottom = bottom_py + flame_h
        mid_inner = bottom_py + int(flame_h * 0.55)
        pygame.draw.polygon(
            self.surface, (255, 160, 40),
            [(left_px, bottom_py), (right_px, bottom_py), (center_x, mid_bottom)],
        )
        pygame.draw.polygon(
            self.surface, (255, 230, 140),
            [(left_px + 5, bottom_py), (right_px - 5, bottom_py), (center_x, mid_inner)],
        )

    def _update_demolish_particles(self, dt):
        dt_sec = dt / 1000.0
        for p in self._demolish_particles[:]:
            p["x"] += p["vx"] * dt_sec
            p["y"] += p["vy"] * dt_sec
            p["vy"] += 600 * dt_sec
            p["vx"] *= 0.96
            p["life"] -= dt
            if p["life"] <= 0:
                self._demolish_particles.remove(p)

    def _draw_demolish_particles(self):
        for p in self._demolish_particles:
            t = p["life"] / p["max_life"]
            alpha = int(max(0, t * 220))
            r = max(1, int(p["size"] * (0.3 + 0.7 * t)))
            color = (min(255, p["color"][0]),
                     min(255, p["color"][1]),
                     min(255, p["color"][2]))
            pygame.draw.circle(
                self.surface, color + (alpha,),
                (int(p["x"]), int(p["y"])), r,
            )

    def _draw_drop_particles(self):
        for p in self._drop_particles:
            t = p["life"] / p["max_life"]
            alpha = int(max(0, t * 200))
            size = max(1, int(p["size"] * (0.3 + 0.7 * t)))
            color = (min(255, p["color"][0]),
                     min(255, p["color"][1]),
                     min(255, p["color"][2]))
            pygame.draw.circle(
                self.surface, color + (alpha,),
                (int(p["x"]), int(p["y"])), size,
            )

    # ── update ────────────────────────────────────────────────────────

    def update(self, dt):
        self._update_snow(dt)
        self._update_stars(dt)
        self._update_falling_buildings(dt)
        self._update_demolish_particles(dt)
        self.cat.update(dt)
        self.building_menu.money = self.money
        self.building_menu.visible = self.mode == "CONSTRUCT"
        px, py = pygame.mouse.get_pos()
        if self._is_over_widget((px, py)) or self._mode_rect.collidepoint((px, py)) or self._mine_rect.collidepoint((px, py)) or self._alien_rect.collidepoint((px, py)):
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
        self.cat.draw(self.surface)
        self._draw_falling_buildings()
        self._draw_drop_particles()
        self._draw_demolish_particles()
        self._draw_snow()
        self.grid.draw(self.surface)
        self._draw_hover()
        for widget in self.widgets:
            widget.draw(self.surface)
        self._draw_mode_toggle()
        self._draw_mine_button()
        self._draw_alien_button()
        self._draw_money()
        if config.debug_cat_state:
            try:
                state = self.cat.get_state()
                txt = f"CAT {state['behavior']} ({state['anim']})"
                font = pygame.font.Font(None, 20)
                label = font.render(txt, True, (255, 255, 255))
                self.surface.blit(label, (10, 40))
            except Exception:
                pass

    def _draw_building(self, surface, bt, px, py, alpha=255):
        """Draw a building — sprite if available, colored rect as fallback."""
        sprite = building_sprites.get(bt["name"])
        print(f"[DRAW] {bt['name']} sprite={sprite is not None}")
        w_px = bt["w"] * config.GRID_CELL_SIZE
        h_px = bt["h"] * config.GRID_CELL_SIZE
        if sprite:
            img = sprite
            if alpha < 255:
                img = sprite.copy()
                img.set_alpha(alpha)
            surface.blit(img, (px, py))
        else:
            # Fallback: colored rectangle
            color = bt["color"]
            rect = pygame.Rect(px, py, w_px, h_px)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)

    def _draw_buildings(self):
        for b in self.buildings:
            bt = next(t for t in config.BUILDING_TYPES if t["name"] == b["type"])
            # Get pixel position of the building's bottom-left cell
            px, py = self.grid.grid_to_pixel(b["gx"], b["gy"])
            # Shift py up so the sprite covers the full height
            py = py - (bt["h"] - 1) * config.GRID_CELL_SIZE
            self._draw_building(self.surface, bt, px, py)

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

    def _draw_mine_button(self):
        bg = (70, 80, 140)
        pygame.draw.rect(self.surface, bg, self._mine_rect)
        pygame.draw.rect(self.surface, (150, 160, 200), self._mine_rect, 1)
        label = self._mine_font.render("Mine Asteroids", True, (220, 225, 255))
        tx = self._mine_rect.x + (self._mine_rect.w - label.get_width()) // 2
        ty = self._mine_rect.y + (self._mine_rect.h - label.get_height()) // 2
        self.surface.blit(label, (tx, ty))

    def _draw_alien_button(self):
        bg = (100, 60, 120)
        pygame.draw.rect(self.surface, bg, self._alien_rect)
        pygame.draw.rect(self.surface, (180, 150, 200), self._alien_rect, 1)
        label = self._mine_font.render("Alien Evasion", True, (220, 215, 240))
        tx = self._alien_rect.x + (self._alien_rect.w - label.get_width()) // 2
        ty = self._alien_rect.y + (self._alien_rect.h - label.get_height()) // 2
        self.surface.blit(label, (tx, ty))

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
            self._ensure_ground()
            if config.debug:
                print(f"[LOAD] loaded {len(self.buildings)} buildings, money={self.money}")
        except (json.JSONDecodeError, KeyError) as e:
            if config.debug:
                print(f"[LOAD] failed: {e}")

    def _ensure_ground(self):
        has_ground = any(b["type"] == "Ground" for b in self.buildings)
        if has_ground:
            return
        ground = config.generate_ground_layers()
        bt_map = {bt["name"]: bt for bt in config.BUILDING_TYPES}
        for entry in ground:
            if (entry["gx"], entry["gy"]) in self._occupied_cells:
                continue
            bt = bt_map[entry["type"]]
            self.buildings.append({
                "type": bt["name"],
                "gx": entry["gx"],
                "gy": entry["gy"],
                "width": bt["w"],
                "height": bt["h"],
                "color": bt["color"],
                "cost": bt["cost"],
            })
            self._occupied_cells.add((entry["gx"], entry["gy"]))
        if config.debug:
            print(f"[LOAD] generated ground tiles for old save")

    def get_debug_info(self):
        return f"[LEVEL] LevelLight | buildings={len(self.buildings)} money={self.money}"
