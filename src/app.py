import pygame
from src import config
from src.debug import DebugManager
from src.animations.sprites import AnimatedSprite
from src.ui.menu import (
    update_menus, draw_menus, get_action, clear_action, enable_main_menu,
    open_pause_menu, get_pause_action, clear_pause_action,
)
from src.ui import menu as menu_module
from src.ui import spinner
from src import audio
from src.levels.light.level_light import LevelLight
from src.levels.dark.level_dark import LevelDark
from src.levels.dark_2.level_dark2 import LevelDark2


class App:
    """Main game application managing states, levels, and the game loop."""
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"

        self.dm = DebugManager()
        if config.debug:
            self.dm.add_source("APP", self.get_debug_info)
            self.dm.add_source("AUDIO", audio.get_debug_info)
            self.dm.add_source("MENU", menu_module.get_debug_info)

        self.moon_sprite = AnimatedSprite()
        self.sprite_group = pygame.sprite.Group(self.moon_sprite)

        self._trans_timer = 0
        self.level = None
        self._minigame = False
        self._saved_level = None

        spinner.init()

    def run(self):
        """Run the main game loop until the application quits."""
        while self.running:
            dt = self.clock.tick(60)
            config.set_fps(self.clock.get_fps())

            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.state == "MENU":
                self._update_menu(dt, events)
            elif self.state == "TRANSITION":
                self._update_transition(dt, events)
            elif self.state == "PLAYING":
                self._update_playing(dt, events)
            elif self.state == "PAUSED":
                self._update_paused(dt, events)

            self.dm.update(dt)
            spinner.update(dt)
            if spinner.is_active():
                spinner.draw(self.surface)
            pygame.display.flip()

    def _update_menu(self, dt, events):
        """Handle logic and rendering while in the MENU state."""
        self.moon_sprite.update(dt)
        update_menus(events)

        action = get_action()
        if action == "LOAD":
            clear_action()
            if config.debug and config.debug_app:
                print("[APP] MENU → TRANSITION (LOAD)")
            spinner.start("Loading game...")
            self._trans_timer = 2000
            self.state = "TRANSITION"
            return
        if action == "NEW":
            clear_action()
            if config.debug and config.debug_app:
                print("[APP] MENU → TRANSITION (NEW)")
            spinner.start("Starting new game...")
            self._trans_timer = 2000
            self.state = "TRANSITION"
            return

        self.surface.fill(config.COLOR_BACKGROUND)
        self.sprite_group.draw(self.surface)
        draw_menus(self.surface)

    def get_debug_info(self):
        """Return a debug string with current app state and FPS."""
        f = config.get_fps()
        return (f"[APP] state={self.state} fps={f:.0f} "
                f"minigame={self._minigame}")

    def _update_transition(self, dt, events):
        """Handle the transition timer then switch to the PLAYING state."""
        self._trans_timer -= dt
        if self._trans_timer <= 0:
            spinner.stop()
            if config.debug and config.debug_app:
                print("[APP] TRANSITION → PLAYING")
            self.level = LevelLight(self.surface, config.get_save_name(), dm=self.dm)
            audio.play_music_file(config.LIGHT_MUSIC)
            self.state = "PLAYING"

    def _update_playing(self, dt, events):
        """Handle gameplay logic and input while in the PLAYING state."""
        if self._minigame:
            self._update_minigame(dt, events)
            return
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if config.debug and config.debug_app:
                    print("[APP] PLAYING → PAUSED (ESC)")
                open_pause_menu()
                self.state = "PAUSED"
                return
            self.level.handle_event(event)

        self.level.update(dt)
        self.level.draw()

        if config.get_mine_requested():
            config.clear_mine_requested()
            self._enter_minigame()
        if config.get_alien_requested():
            config.clear_alien_requested()
            self._enter_alien_minigame()

    def _enter_minigame(self):
        """Switch to the dark-side mining minigame, saving the current level."""
        if config.debug and config.debug_app:
            print("[APP] entering dark side minigame")
        audio.play_music_file(config.DARK_MUSIC)
        self._saved_level = self.level
        self._minigame = True
        self.level = LevelDark(self.surface, minigame=True, dm=self.dm)

    def _enter_alien_minigame(self):
        """Switch to the alien evasion minigame, saving the current level."""
        if config.debug and config.debug_app:
            print("[APP] entering alien evasion minigame")
        audio.play_music_file(config.DARK_MUSIC)
        self._saved_level = self.level
        self._minigame = True
        self.level = LevelDark2(self.surface, minigame=True, dm=self.dm)

    def _exit_minigame(self):
        """Return from the minigame and add earnings to the main level."""
        earnings = self.level.score
        if config.debug and config.debug_app:
            print(f"[APP] _exit_minigame: earnings={earnings}")
        audio.play_music_file(config.LIGHT_MUSIC)
        if isinstance(self._saved_level, LevelLight):
            self._saved_level.money += earnings
            if config.debug:
                print(f"[APP] added {earnings} coins to light level, total={self._saved_level.money}")
        elif config.debug:
            print(f"[APP] WARNING: _saved_level is not LevelLight, type={type(self._saved_level).__name__}")
        self.level = self._saved_level
        self._saved_level = None
        self._minigame = False

    def _update_minigame(self, dt, events):
        """Handle active minigame update loop and check for completion."""
        for event in events:
            self.level.handle_event(event)
        self.level.update(dt)
        self.level.draw()
        if self.level.is_minigame_done():
            self._exit_minigame()

    def _update_paused(self, dt, events):
        """Handle pause menu input and overlay rendering."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if config.debug and config.debug_app:
                    print("[APP] PAUSED → PLAYING (ESC)")
                clear_pause_action()
                self.state = "PLAYING"
                return

        update_menus(events)

        action = get_pause_action()
        if action == "CONTINUE":
            clear_pause_action()
            if config.debug and config.debug_app:
                print("[APP] PAUSED → PLAYING")
            self.state = "PLAYING"
            return
        if action == "QUIT":
            clear_pause_action()
            if config.debug and config.debug_app:
                print("[APP] PAUSED → MENU")
            audio.stop_music()
            enable_main_menu()
            self.level = None
            self.state = "MENU"
            return

        self.level.draw()
        dim = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        dim.set_alpha(128)
        dim.fill((0, 0, 0))
        self.surface.blit(dim, (0, 0))
        draw_menus(self.surface)
