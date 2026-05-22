import pygame
from src import config
from src.sprites import AnimatedSprite
from src.menu import (
    update_menus, draw_menus, get_action, clear_action, enable_main_menu,
    open_pause_menu, get_pause_action, clear_pause_action,
)
from src import spinner
from src import audio
from src.levels.level_light import LevelLight
from src.levels.level_dark import LevelDark


class App:
    def __init__(self, surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"

        self.moon_sprite = AnimatedSprite()
        self.sprite_group = pygame.sprite.Group(self.moon_sprite)

        self._trans_timer = 0
        self.level = None
        self._minigame = False
        self._saved_level = None

        spinner.init()

    def run(self):
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

            spinner.update(dt)
            if spinner.is_active():
                spinner.draw(self.surface)
            pygame.display.flip()

    def _update_menu(self, dt, events):
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

    def _update_transition(self, dt, events):
        self._trans_timer -= dt
        if self._trans_timer <= 0:
            spinner.stop()
            if config.debug and config.debug_app:
                print("[APP] TRANSITION → PLAYING")
            self.level = LevelLight(self.surface, config.get_save_name())
            audio.play_music("11")
            self.state = "PLAYING"

    def _update_playing(self, dt, events):
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

    def _enter_minigame(self):
        if config.debug and config.debug_app:
            print("[APP] entering dark side minigame")
        self._saved_level = self.level
        self._minigame = True
        self.level = LevelDark(self.surface, minigame=True)

    def _exit_minigame(self):
        earnings = self.level.score
        if config.debug and config.debug_app:
            print(f"[APP] exiting dark side minigame, earnings={earnings}")
        if isinstance(self._saved_level, LevelLight):
            self._saved_level.money += earnings
            if config.debug:
                print(f"[APP] added {earnings} coins to light level, total={self._saved_level.money}")
        self.level = self._saved_level
        self._saved_level = None
        self._minigame = False

    def _update_minigame(self, dt, events):
        for event in events:
            self.level.handle_event(event)
        self.level.update(dt)
        self.level.draw()
        if self.level.is_minigame_done():
            self._exit_minigame()

    def _update_paused(self, dt, events):
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
