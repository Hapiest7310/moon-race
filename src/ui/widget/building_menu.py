import pygame
from src import config
from src.ui.widget import Widget
import src.animations.building_sprites as building_sprites


class BuildingMenu(Widget):
    """A widget for selecting buildings to place on the map."""
    BTN_W = 56
    BTN_H = 48

    def __init__(self, rect):
        """Initialise the building menu with its rectangular area."""
        super().__init__(rect)
        self.selected_index = 0
        self.money = 0
        self._padding = 4
        self._name_font = pygame.font.Font(None, 14)
        self._cost_font = pygame.font.Font(None, 16)
        self._buildable_types = [bt for bt in config.BUILDING_TYPES if not bt.get("indestructible")]
        self._build_buttons()

    def _build_buttons(self):
        """Create placeholder rects for each buildable type."""
        self._button_rects = []
        for _ in self._buildable_types:
            self._button_rects.append(pygame.Rect(0, 0, self.BTN_W, self.BTN_H))

    def select_by_key(self, key_number):
        """Select a building by its numeric key (1-based)."""
        idx = key_number - 1
        if 0 <= idx < len(self._buildable_types):
            self.selected_index = idx
            return True
        return False

    def get_selected_building(self):
        """Return the currently selected building type."""
        return self._buildable_types[self.selected_index]

    def _get_layout(self):
        """Calculate the on-screen positions for each building button."""
        n = len(self._button_rects)
        total_w = sum(r.w for r in self._button_rects) + (n - 1) * self._padding
        start_x = (self.rect.width - total_w) // 2
        y = 4
        positions = []
        cx = start_x
        for r in self._button_rects:
            positions.append(pygame.Rect(cx, y, r.w, r.h))
            cx += r.w + self._padding
        return positions

    def handle_event(self, event):
        """Handle mouse clicks to select a building from the menu."""
        if not self.visible or event.type != pygame.MOUSEBUTTONDOWN:
            return False
        if not self.rect.collidepoint(event.pos):
            return False
        lx = event.pos[0] - self.rect.x
        ly = event.pos[1] - self.rect.y
        positions = self._get_layout()
        for i, btn_rect in enumerate(positions):
            if btn_rect.collidepoint(lx, ly):
                self.selected_index = i
                return True
        return False

    def draw(self, surface):
        """Draw the building selection buttons onto the surface."""
        if not self.visible:
            return
        positions = self._get_layout()
        for i, local_rect in enumerate(positions):
            bt = self._buildable_types[i]
            r = pygame.Rect(
                self.rect.x + local_rect.x,
                self.rect.y + local_rect.y,
                local_rect.w, local_rect.h,
            )

            pygame.draw.rect(surface, (40, 40, 40), r)
            if i == self.selected_index:
                pygame.draw.rect(surface, (255, 255, 255), r, 3)
            else:
                pygame.draw.rect(surface, (80, 80, 80), r, 1)

            pw = max(bt["w"] * 8, 16)
            ph = max(bt["h"] * 6, 16)
            preview_rect = pygame.Rect(0, 0, pw, ph)
            preview_rect.center = r.center
            sprite = building_sprites.get(bt["name"])
            if sprite:
                # scale sprite to fit inside the button
                max_w = self.BTN_W - 8
                max_h = self.BTN_H - 16  # leave room for cost text below and size label
                scale = min(max_w / sprite.get_width(), max_h / sprite.get_height())
                scaled_w = max(1, int(sprite.get_width() * scale))
                scaled_h = max(1, int(sprite.get_height() * scale))
                preview = pygame.transform.smoothscale(sprite, (scaled_w, scaled_h))
                px = r.x + (r.w - scaled_w) // 2
                py = r.y + (r.h - scaled_h) // 2 - 4
                surface.blit(preview, (px, py))
            else:
                # fallback colored rect
                pw = max(bt["w"] * 8, 16)
                ph = max(bt["h"] * 6, 16)
                preview_rect = pygame.Rect(0, 0, pw, ph)
                preview_rect.center = r.center
                pygame.draw.rect(surface, bt["color"], preview_rect)

            label = self._name_font.render(f"{bt['w']}x{bt['h']}", True, (180, 180, 180))
            lx = r.x + (r.w - label.get_width()) // 2
            ly = r.y + r.h - label.get_height() - 2
            surface.blit(label, (lx, ly))

            cost_color = (255, 255, 255) if self.money >= bt["cost"] else (200, 50, 50)
            cost_text = self._cost_font.render(str(bt["cost"]), True, cost_color)
            cx = r.x + (r.w - cost_text.get_width()) // 2
            cy = r.y + r.h + 2
            surface.blit(cost_text, (cx, cy))

    def get_debug_info(self):
        """Return a debug string including the selected building info."""
        base = super().get_debug_info()
        bt = self.get_selected_building()
        return f"{base} | selected={bt['name']} cost={bt['cost']}"
