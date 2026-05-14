import pygame
import pygame_menu
from src import config
from src.levels.level_base import Level
from src.grid import Grid
from src.widget.color_picker import ColorPicker


class LevelLight(Level):
    def __init__(self, surface):
        super().__init__(surface)
        self.grid = Grid()
        self.cell_colors = {}
        self._hover_cell = None

        self.color_picker = ColorPicker(pygame.Rect(10, config.SCREEN_HEIGHT - 50, 300, 40))
        self.widgets = [self.color_picker]

        self._last_gx = -1
        self._last_gy = -1

        self._hover_font = pygame.font.Font(None, 18)
        self._hover_surf = pygame.Surface((self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA)

        theme = pygame_menu.themes.THEME_DARK.copy()
        theme.background_color = (30, 30, 50)
        theme.title_bar_visible = False
        theme.widget_margin = (4, 2)

        self.overlay = pygame_menu.Menu(
            "", 520, 170,
            theme=theme,
            enabled=True,
            mouse_visible=False,
        )
        self._debug_labels = []
        for _ in range(6):
            lbl = self.overlay.add.label("", font_size=18, align=pygame_menu.locals.ALIGN_LEFT)
            self._debug_labels.append(lbl)
        self._overlay_rect = pygame.Rect(10, 10, 520, 170)

    # ── layer targeting ──────────────────────────────────────────────

    def _is_over_widget(self, pos):
        for w in self.widgets:
            if w.visible and w.rect.collidepoint(pos):
                return True
        return self._overlay_rect.collidepoint(pos)

    # ── events ────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for widget in self.widgets:
                if widget.handle_event(event):
                    return
            if self._is_over_widget(event.pos):
                return
            gx, gy = self.grid.pixel_to_grid(*event.pos)
            if self.grid.is_in_bounds(gx, gy):
                color = self.color_picker.get_selected_color()
                self.cell_colors[(gx, gy)] = color
                if config.debug and config.debug_cells:
                    print(f"[PAINT] cell ({gx}, {gy}) -> {color}  total={len(self.cell_colors)}")

    # ── update ────────────────────────────────────────────────────────

    def update(self, dt):
        px, py = pygame.mouse.get_pos()
        if self._is_over_widget((px, py)):
            self._hover_cell = None
        else:
            gx, gy = self.grid.pixel_to_grid(px, py)
            self._hover_cell = (gx, gy) if self.grid.is_in_bounds(gx, gy) else None

        if config.debug and config.debug_mouse:
            gx, gy = self.grid.pixel_to_grid(px, py)
            if (gx, gy) != (self._last_gx, self._last_gy):
                self._last_gx, self._last_gy = gx, gy
                print(f"[MOUSE] pixel ({px}, {py}) -> grid ({gx}, {gy})")

    # ── draw ──────────────────────────────────────────────────────────

    def draw(self):
        self.surface.fill((20, 25, 40))
        self._draw_painted_cells()
        self.grid.draw(self.surface)
        self._draw_hover()

        for widget in self.widgets:
            widget.draw(self.surface)
            if config.debug and config.debug_widgets:
                pygame.draw.rect(self.surface, (0, 255, 0), widget.rect, 1)

        self._draw_layout_overlay()
        self._draw_overlay()

    def _draw_painted_cells(self):
        for (gx, gy), color in self.cell_colors.items():
            px, py = self.grid.grid_to_pixel(gx, gy)
            rect = pygame.Rect(px, py, self.grid.cell_size, self.grid.cell_size)
            pygame.draw.rect(self.surface, color, rect)

    def _draw_hover(self):
        if not self._hover_cell:
            return
        gx, gy = self._hover_cell
        px, py = self.grid.grid_to_pixel(gx, gy)
        rect = pygame.Rect(px, py, self.grid.cell_size, self.grid.cell_size)
        self._hover_surf.fill((255, 255, 255, 60))
        self.surface.blit(self._hover_surf, rect)

        if config.debug and config.debug_hover:
            label = self._hover_font.render(f"({gx}, {gy})", True, (255, 255, 200))
            lx = px + (self.grid.cell_size - label.get_width()) // 2
            ly = py + (self.grid.cell_size - label.get_height()) // 2
            self.surface.blit(label, (lx, ly))

    def _draw_layout_overlay(self):
        if not (config.debug and config.debug_layout):
            return
        grid_top = config.SCREEN_HEIGHT - self.grid.rows * self.grid.cell_size
        grid_rect = pygame.Rect(0, grid_top, config.SCREEN_WIDTH, config.SCREEN_HEIGHT - grid_top)
        pygame.draw.rect(self.surface, (50, 100, 200), grid_rect, 2)
        for w in self.widgets:
            pygame.draw.rect(self.surface, (0, 255, 100), w.rect, 2)
        pygame.draw.rect(self.surface, (200, 200, 50), self._overlay_rect, 2)

    def _draw_overlay(self):
        lines = [""] * 6
        if config.debug:
            if config.debug_fps:
                lines[0] = f"FPS: {config.get_fps():.0f}"
            if config.debug_app:
                lines[0] += f"  |  state: PLAYING  level: Light Side"

            if config.debug_mouse:
                px, py = pygame.mouse.get_pos()
                gx, gy = self.grid.pixel_to_grid(px, py)
                lines[1] = f"pixel: ({px}, {py})  grid: ({gx}, {gy})"

            if config.debug_hover:
                if self._hover_cell:
                    lines[2] = f"hover: ({self._hover_cell[0]}, {self._hover_cell[1]})"
                else:
                    lines[2] = "hover: ---"

            if config.debug_widgets:
                parts = []
                for w in self.widgets:
                    parts.append(w.get_debug_info())
                lines[3] = " | ".join(parts)

            if config.debug_cells:
                lines[4] = f"painted cells: {len(self.cell_colors)}"

            lines[5] = f"grid: {self.grid.cols}c x {self.grid.rows}r"

        for i, lbl in enumerate(self._debug_labels):
            lbl.set_title(lines[i])
        self.overlay.draw(self.surface.subsurface(self._overlay_rect))

    def get_debug_info(self):
        return f"[LEVEL] LevelLight | painted_cells={len(self.cell_colors)}"
