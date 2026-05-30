import pygame


class ShaderSurface:
    """A compositable surface with blend-mode blitting for shader-like effects."""

    __slots__ = ("surface",)

    BLEND_NORMAL = -1
    BLEND_ADD = pygame.BLEND_ADD

    def __init__(self, width, height):
        """Initialise the surface with the given dimensions and SRCALPHA."""
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def clear(self):
        """Fill the entire surface with fully transparent black."""
        self.surface.fill((0, 0, 0, 0))

    def blit_to(self, target, pos=(0, 0), blend=None):
        """Blit this surface onto *target* at *pos* with an optional blend mode."""
        if blend is not None and blend != self.BLEND_NORMAL:
            target.blit(self.surface, pos, None, blend)
        else:
            target.blit(self.surface, pos)
