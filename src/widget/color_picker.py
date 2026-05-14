import pygame
from src.widget import Widget


class ColorPicker(Widget):
    COLORS = [
        (255, 50, 50),
        (255, 165, 50),
        (255, 255, 50),
        (50, 255, 50),
        (50, 255, 255),
        (50, 50, 255),
        (200, 50, 255),
        (255, 255, 255),
    ]

    def __init__(self, rect):
        super().__init__(rect)
        self.selected_index = 0
        self._padding = 5
        self._btn_size = self.rect.height - 2 * self._padding
        self._build_buttons()

    def _build_buttons(self):
        n = len(self.COLORS)
        total = n * self._btn_size + (n - 1) * self._padding
        start_x = (self.rect.width - total) // 2
        self._button_rects = []
        for i in range(n):
            x = start_x + i * (self._btn_size + self._padding)
            y = self._padding
            self._button_rects.append(pygame.Rect(x, y, self._btn_size, self._btn_size))

    def get_selected_color(self):
        return self.COLORS[self.selected_index]

    def handle_event(self, event):
        if not self.visible or event.type != pygame.MOUSEBUTTONDOWN:
            return False
        if not self.rect.collidepoint(event.pos):
            return False
        lx = event.pos[0] - self.rect.x
        ly = event.pos[1] - self.rect.y
        for i, btn in enumerate(self._button_rects):
            if btn.collidepoint(lx, ly):
                self.selected_index = i
                return True
        return False

    def draw(self, surface):
        if not self.visible:
            return
        for i, btn in enumerate(self._button_rects):
            abs_rect = btn.move(self.rect.x, self.rect.y)
            pygame.draw.rect(surface, self.COLORS[i], abs_rect)
            if i == self.selected_index:
                pygame.draw.rect(surface, (255, 255, 255), abs_rect, 3)
            else:
                pygame.draw.rect(surface, (80, 80, 80), abs_rect, 1)

    def get_debug_info(self):
        base = super().get_debug_info()
        return f"{base} | selected={self.selected_index} color={self.COLORS[self.selected_index]}"
