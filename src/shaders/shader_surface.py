import pygame


class ShaderSurface:
    """Draw shapes onto an SRCALPHA surface, then blit with a blend mode.

    This acts as a lightweight 'shader' layer — each ShaderSurface can
    be composited onto the final frame using pygame blend modes such as
    BLEND_ADD (for glow) or BLEND_ALPHA_SDL2.

    To swap in real GLSL shaders: replace pygame.Surface with an
    OpenGL framebuffer and apply shader programs during blit_to().
    """

    __slots__ = ("surface",)

    BLEND_NORMAL = -1
    BLEND_ADD = pygame.BLEND_ADD
    BLEND_MULT = pygame.BLEND_MULT
    BLEND_ALPHA = pygame.BLEND_ALPHA_SDL2

    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def clear(self):
        self.surface.fill((0, 0, 0, 0))

    def fill(self, color):
        self.surface.fill(color)

    def blit_to(self, target, pos=(0, 0), blend=None):
        if blend is not None and blend != self.BLEND_NORMAL:
            target.blit(self.surface, pos, None, blend)
        else:
            target.blit(self.surface, pos)

    def circle(self, color, pos, radius, width=0):
        pygame.draw.circle(self.surface, color, (int(pos[0]), int(pos[1])),
                           int(radius), width)

    def polygon(self, color, points, width=0):
        pygame.draw.polygon(
            self.surface, color,
            [(int(x), int(y)) for x, y in points], width,
        )

    def line(self, color, start, end, width=1):
        pygame.draw.line(
            self.surface, color,
            (int(start[0]), int(start[1])),
            (int(end[0]), int(end[1])), width,
        )
