import pygame_menu
from pygame_menu import events
from pygame_menu.locals import ALIGN_CENTER
from src import config

_main_menu = None
_start_menu = None
_options_menu = None
_next_action = "NONE"


def create_menus():
    global _main_menu, _start_menu, _options_menu

    _main_menu = pygame_menu.Menu(
        "Moon Race", 400, 300, theme=pygame_menu.themes.THEME_DARK
    )
    _main_menu.add.button("Start", _open_start)
    _main_menu.add.button("Options", _open_options)
    _main_menu.add.button("Quit", events.EXIT)

    _start_menu = pygame_menu.Menu(
        "Start", 400, 300, theme=pygame_menu.themes.THEME_DARK
    )
    _start_menu.disable()
    _start_menu.add.button("Load", _set_load)
    _start_menu.add.button("New", _set_new)
    _start_menu.add.button("Back", _back_to_main)

    _options_menu = pygame_menu.Menu(
        "Options", 400, 300, theme=pygame_menu.themes.THEME_DARK
    )
    _options_menu.disable()
    _options_menu.add.button("Keybindings", _show_keybindings)
    _options_menu.add.button("Sound", _show_sound)
    _options_menu.add.button("Back", _back_to_main)


def get_main_menu():
    return _main_menu


def _open_start():
    _main_menu.disable()
    _start_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] main → start")


def _open_options():
    _main_menu.disable()
    _options_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] main → options")


def _back_to_main():
    _start_menu.disable()
    _options_menu.disable()
    _main_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] * → main")


def _set_load():
    global _next_action
    _next_action = "LOAD"
    _start_menu.disable()
    if config.debug and config.debug_menu:
        print("[MENU] action set: LOAD")


def _set_new():
    global _next_action
    _next_action = "NEW"
    _start_menu.disable()
    if config.debug and config.debug_menu:
        print("[MENU] action set: NEW")


def _show_keybindings():
    print("Keybindings — not implemented yet")


def _show_sound():
    print("Sound — not implemented yet")


def get_action():
    return _next_action


def clear_action():
    global _next_action
    _next_action = "NONE"


def enable_main_menu():
    _start_menu.disable()
    _options_menu.disable()
    _main_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] enable main menu")


def update_menus(events_list):
    if _main_menu.is_enabled():
        _main_menu.update(events_list)
    if _start_menu.is_enabled():
        _start_menu.update(events_list)
    if _options_menu.is_enabled():
        _options_menu.update(events_list)


def draw_menus(surface):
    if _main_menu.is_enabled():
        _main_menu.draw(surface)
    if _start_menu.is_enabled():
        _start_menu.draw(surface)
    if _options_menu.is_enabled():
        _options_menu.draw(surface)
