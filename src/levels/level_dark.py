import pygame
from src import config
from src.levels.level_base import Level


class LevelDark(Level):
    def __init__(self, surface):
        super().__init__(surface)

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        self.surface.fill((10, 10, 20))

    def get_debug_info(self):
        return f"[LEVEL] LevelDark"
