import pygame


class Widget:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.visible = True

    def handle_event(self, event):
        return False

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def get_debug_info(self):
        if not self.visible:
            return f"[WIDGET] {type(self).__name__} — disabled"
        return f"[WIDGET] {type(self).__name__} — rect=({self.rect.x}, {self.rect.y}, {self.rect.w}, {self.rect.h})"
