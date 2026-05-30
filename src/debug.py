from src import config


class DebugManager:
    """Periodically prints debug info from registered sources."""
    def __init__(self):
        self._sources = []
        self._accum = 0

    def add_source(self, name, getter):
        """Register a debug info source with a name and getter callable."""
        self._sources.append((name, getter))

    def update(self, dt):
        """Accumulate delta time and print sources when interval elapses."""
        if not config.debug:
            return
        if not self._sources:
            return
        self._accum += dt
        if self._accum < config.DEBUG_PRINT_INTERVAL:
            return
        self._accum = 0
        for name, getter in self._sources:
            try:
                info = getter()
                if info:
                    print(info)
            except Exception:
                pass
