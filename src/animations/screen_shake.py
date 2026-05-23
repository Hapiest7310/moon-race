import random


class ScreenShake:
    """Camera offset effect triggered on impacts / explosions."""

    def __init__(self):
        self.timer = 0.0
        self.intensity = 0.0
        self.offset = [0, 0]

    def trigger(self, intensity, duration=None):
        if duration is None:
            duration = intensity * 2.5
        self.timer = min(self.timer + duration, 300)
        self.intensity = max(self.intensity, min(intensity, 14))

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            self.offset[0] = random.uniform(-self.intensity, self.intensity)
            self.offset[1] = random.uniform(-self.intensity, self.intensity)
            self.intensity *= 0.92
        else:
            self.offset = [0, 0]
            self.intensity = 0.0

    def clear(self):
        self.timer = 0.0
        self.intensity = 0.0
        self.offset = [0, 0]
