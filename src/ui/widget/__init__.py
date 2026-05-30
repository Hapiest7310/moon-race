"""Base widget classes for the UI system."""

import pygame


class Widget:
    """Base class for all UI widgets."""
    def __init__(self, rect):
        """Initialise the widget with a rectangular area."""
        self.rect = pygame.Rect(rect)
        self.visible = True

    def handle_event(self, event):
        """Handle a pygame event; return True if consumed."""
        return False

    def draw(self, surface):
        """Draw the widget onto the given surface."""
        pass

    def get_debug_info(self):
        """Return a debug string describing the widget's state."""
        if not self.visible:
            return f"[WIDGET] {type(self).__name__} — disabled"
        return f"[WIDGET] {type(self).__name__} — rect=({self.rect.x}, {self.rect.y}, {self.rect.w}, {self.rect.h})"
