import pygame


class Level:
    def __init__(self, surface):
        self.surface = surface
        self.done = False

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

    def get_debug_info(self):
        return f"[LEVEL] {type(self).__name__}"
