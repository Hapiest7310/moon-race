import pygame
from src import config


class Grid:
    def __init__(self):
        self.cell_size = config.GRID_CELL_SIZE
        self.cols = config.GRID_COLS
        self.rows = config.GRID_ROWS

    def grid_to_pixel(self, gx, gy):
        px = gx * self.cell_size
        py = config.SCREEN_HEIGHT - (gy + 1) * self.cell_size
        return px, py

    def pixel_to_grid(self, px, py):
        gx = px // self.cell_size
        gy = (config.SCREEN_HEIGHT - py - 1) // self.cell_size
        return int(gx), int(gy)

    def is_in_bounds(self, gx, gy):
        return 0 <= gx < self.cols and 0 <= gy < self.rows

    def draw(self, surface):
        if not (config.show_grid or (config.debug and config.debug_grid)):
            return
        grid_bottom = config.SCREEN_HEIGHT
        grid_top = config.SCREEN_HEIGHT - self.rows * self.cell_size

        color = (50, 50, 80)
        for i in range(self.cols + 1):
            x = i * self.cell_size
            pygame.draw.line(surface, color, (x, grid_top), (x, grid_bottom))
        for i in range(self.rows + 1):
            y = config.SCREEN_HEIGHT - i * self.cell_size
            pygame.draw.line(surface, color, (0, y), (config.SCREEN_WIDTH, y))

        pygame.draw.rect(surface, (50, 100, 150), (0, grid_top, config.SCREEN_WIDTH, grid_bottom - grid_top), 1)

        font = pygame.font.Font(None, 20)
        info = font.render(
            f"grid: {self.cols}c x {self.rows}r  cell={self.cell_size}px",
            True, (80, 130, 180)
        )
        surface.blit(info, (10, config.SCREEN_HEIGHT - 20))
