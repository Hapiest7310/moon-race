import pygame
from src import config
from src.widget import Widget


class BuildingMenu(Widget):
    def __init__(self, rect):
        super().__init__(rect)
        self.selected_index = 0
        self.money = 0
        self._padding = 4
        self._name_font = pygame.font.Font(None, 14)
        self._cost_font = pygame.font.Font(None, 16)
        self._build_buttons()

    def _build_buttons(self):
        self._button_rects = []
        for bt in config.BUILDING_TYPES:
            bw = bt["w"] * 10 + 16
            bh = bt["h"] * 8 + 10
            bw = max(bw, 28)
            bh = max(bh, 24)
            self._button_rects.append(pygame.Rect(0, 0, bw, bh))

    def get_selected_building(self):
        return config.BUILDING_TYPES[self.selected_index]

    def _get_layout(self):
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
        if not self.visible:
            return
        positions = self._get_layout()
        for i, local_rect in enumerate(positions):
            bt = config.BUILDING_TYPES[i]
            r = pygame.Rect(
                self.rect.x + local_rect.x,
                self.rect.y + local_rect.y,
                local_rect.w, local_rect.h,
            )
            pygame.draw.rect(surface, bt["color"], r)
            if i == self.selected_index:
                pygame.draw.rect(surface, (255, 255, 255), r, 3)
            else:
                pygame.draw.rect(surface, (80, 80, 80), r, 1)

            label = self._name_font.render(f"{bt['w']}x{bt['h']}", True, (255, 255, 255))
            lx = r.x + (r.w - label.get_width()) // 2
            ly = r.y + (r.h - label.get_height()) // 2
            surface.blit(label, (lx, ly))

            cost_color = (255, 255, 255) if self.money >= bt["cost"] else (200, 50, 50)
            cost_text = self._cost_font.render(str(bt["cost"]), True, cost_color)
            cx = r.x + (r.w - cost_text.get_width()) // 2
            cy = r.y + r.h + 2
            surface.blit(cost_text, (cx, cy))

    def get_debug_info(self):
        base = super().get_debug_info()
        bt = self.get_selected_building()
        return f"{base} | selected={bt['name']} cost={bt['cost']}"
