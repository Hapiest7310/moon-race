import pygame
import pygame_menu
from pygame_menu import events
from pygame_menu.locals import ALIGN_CENTER


_main_menu = None
_options_menu = None
_level_menu = None


def create_menus():
    global _main_menu, _options_menu, _level_menu

    _main_menu = pygame_menu.Menu(
        "Moon Race", 400, 300, theme=pygame_menu.themes.THEME_DARK
    )

    _main_menu.add.label("MOON RACE", font_size=40, align=ALIGN_CENTER)
    _main_menu.add.button("Start Game", _start_game)
    _main_menu.add.button("Options", _open_options)
    _main_menu.add.button("Quit", events.EXIT)

    _options_menu = pygame_menu.Menu(
        "Options", 400, 300, theme=pygame_menu.themes.THEME_DARK
    )
    _options_menu.disable()

    _options_menu.add.toggle_switch("Sound", True)
    _options_menu.add.toggle_switch("Music", True)
    _options_menu.add.button("Back", events.BACK)

    _level_menu = pygame_menu.Menu(
        "Select Level", 400, 300, theme=pygame_menu.themes.THEME_DARK
    )
    _level_menu.disable()

    _level_menu.add.label("Dark Side", font_size=20, align=ALIGN_CENTER)
    _level_menu.add.button("Play", _start_dark_side)
    _level_menu.add.label("Light Side", font_size=20, align=ALIGN_CENTER)
    _level_menu.add.button("Play", _start_light_side)
    _level_menu.add.button("Back", events.BACK)


def get_main_menu():
    return _main_menu


def _start_game():
    _main_menu.disable()
    _level_menu.enable()


def _open_options():
    _main_menu.disable()
    _options_menu.enable()


def _start_dark_side():
    print("Starting Dark Side of the Moon...")


def _start_light_side():
    print("Starting Light Side of the Moon...")


def update_menus(events_list):
    if _main_menu.is_enabled():
        _main_menu.update(events_list)
    if _options_menu.is_enabled():
        _options_menu.update(events_list)
    if _level_menu.is_enabled():
        _level_menu.update(events_list)


def draw_menus(surface):
    if _main_menu.is_enabled():
        _main_menu.draw(surface)
    if _options_menu.is_enabled():
        _options_menu.draw(surface)
    if _level_menu.is_enabled():
        _level_menu.draw(surface)
