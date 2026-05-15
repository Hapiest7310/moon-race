import json
import os
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

        self._hover_font = pygame.font.Font(None, 18)
        self._money_font = pygame.font.Font(None, 36)
        self._valid_highlight = pygame.Surface(
            (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
        )
        self._invalid_highlight = pygame.Surface(
            (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
        )
        self._valid_highlight.fill((0, 255, 0, 60))
        self._invalid_highlight.fill((255, 0, 0, 60))

        self.load()

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

    # ── events ────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for widget in self.widgets:
                if widget.handle_event(event):
                    return
            if self._is_over_widget(event.pos):
                return
            gx, gy = self.grid.pixel_to_grid(*event.pos)
            if not self.grid.is_in_bounds(gx, gy):
                return
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
        })
        self._occupied_cells.update(cells)
        self.money -= bt["cost"]
        if config.debug:
            print(f"[BUILD] placed {bt['name']} at ({gx},{gy}) money={self.money}")
        self.save()

    # ── update ────────────────────────────────────────────────────────

    def update(self, dt):
        self.building_menu.money = self.money
        px, py = pygame.mouse.get_pos()
        if self._is_over_widget((px, py)):
            self._hover_cell = None
        else:
            gx, gy = self.grid.pixel_to_grid(px, py)
            if self.grid.is_in_bounds(gx, gy):
                self._hover_cell = (gx, gy)
            else:
                self._hover_cell = None

    # ── draw ──────────────────────────────────────────────────────────

    def draw(self):
        self.surface.fill((20, 25, 40))
        self._draw_buildings()
        self.grid.draw(self.surface)
        self._draw_hover()
        for widget in self.widgets:
            widget.draw(self.surface)
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
