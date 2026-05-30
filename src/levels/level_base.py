import pygame


class Level:
    """Base class for all game levels."""
    def __init__(self, surface):
        """Initialize the level with a surface."""
        self.surface = surface
        self.done = False

    def handle_event(self, event):
        """Process an input event for the level."""
        pass

    def update(self, dt):
        """Update the level state each frame."""
        pass

    def draw(self):
        """Render the level to the surface."""
        pass

    def get_debug_info(self):
        """Return a debug string for the level."""
        return f"[LEVEL] {type(self).__name__}"
