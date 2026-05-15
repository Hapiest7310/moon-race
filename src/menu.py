import json
import os
import pygame_menu
from pygame_menu import events
from src import config
from src import audio

_main_menu = None
_start_menu = None
_new_menu = None
_load_menu = None
_options_menu = None
_sound_menu = None
_pause_menu = None
_next_action = "NONE"
_pause_action = "NONE"
_new_name_input = None
_sound_origin = "options"


def _on_music_volume(value):
    audio.set_music_volume(value / 100)


def _on_sfx_volume(value):
    audio.set_sfx_volume(value / 100)


def _list_save_files():
    if not os.path.isdir(config.SAVE_DIR):
        return []
    return sorted(
        f[:-5] for f in os.listdir(config.SAVE_DIR) if f.endswith(".json")
    )


def _refresh_load_menu():
    _load_menu.clear()
    saves = _list_save_files()
    if not saves:
        _load_menu.add.label("No save files found")
    else:
        for name in saves:
            _load_menu.add.button(name, _select_save, name)
    _load_menu.add.button("Back", _back_to_start)


def create_menus():
    global _main_menu, _start_menu, _new_menu, _load_menu
    global _options_menu, _sound_menu, _new_name_input, _pause_menu

    theme = pygame_menu.themes.THEME_DARK

    _main_menu = pygame_menu.Menu("Moon Race", 400, 300, theme=theme)
    _main_menu.add.button("Start", _open_start)
    _main_menu.add.button("Options", _open_options)
    _main_menu.add.button("Quit", events.EXIT)

    _start_menu = pygame_menu.Menu("Start", 400, 300, theme=theme)
    _start_menu.disable()
    _start_menu.add.button("New Game", _open_new_menu)
    _start_menu.add.button("Load Game", _open_load_menu)
    _start_menu.add.button("Back", _back_to_main)

    _new_menu = pygame_menu.Menu("New Game", 400, 300, theme=theme)
    _new_menu.disable()
    _new_name_input = _new_menu.add.text_input("Save name: ", default="", maxchar=24)
    _new_menu.add.button("Confirm", _confirm_new)
    _new_menu.add.button("Back", _back_to_start)

    _load_menu = pygame_menu.Menu("Load Game", 400, 300, theme=theme)
    _load_menu.disable()

    _options_menu = pygame_menu.Menu("Options", 400, 300, theme=theme)
    _options_menu.disable()
    _options_menu.add.button("Keybindings", _show_keybindings)
    _options_menu.add.button("Sound", _open_sound)
    _options_menu.add.button("Back", _back_to_main)

    _sound_menu = pygame_menu.Menu("Sound", 400, 300, theme=theme)
    _sound_menu.disable()
    _sound_menu.add.range_slider(
        "Music Volume",
        int(audio.get_music_volume() * 100),
        (0, 100), 1,
        onchange=_on_music_volume,
    )
    _sound_menu.add.range_slider(
        "SFX Volume",
        int(audio.get_sfx_volume() * 100),
        (0, 100), 1,
        onchange=_on_sfx_volume,
    )
    _sound_menu.add.button("Back", _back_from_sound)

    _pause_menu = pygame_menu.Menu("Paused", 400, 300, theme=theme)
    _pause_menu.disable()
    _pause_menu.add.button("Continue", _continue_game)
    _pause_menu.add.button("Options", _open_sound_from_pause)
    _pause_menu.add.button("Quit", _quit_to_menu)


def get_main_menu():
    return _main_menu


# ── navigation ────────────────────────────────────────────────────────

def _open_start():
    _main_menu.disable()
    _start_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] main → start")


def _open_new_menu():
    _start_menu.disable()
    _new_name_input.set_value("")
    _new_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] start → new")


def _open_load_menu():
    _start_menu.disable()
    _refresh_load_menu()
    _load_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] start → load")


def _open_options():
    _main_menu.disable()
    _options_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] main → options")


def _open_sound():
    global _sound_origin
    _sound_origin = "options"
    _options_menu.disable()
    _sound_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] options → sound")


def _open_sound_from_pause():
    global _sound_origin
    _sound_origin = "pause"
    _pause_menu.disable()
    _sound_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] pause → sound")


def _back_to_start():
    _new_menu.disable()
    _load_menu.disable()
    _start_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] * → start")


def _back_to_main():
    _start_menu.disable()
    _new_menu.disable()
    _load_menu.disable()
    _options_menu.disable()
    _sound_menu.disable()
    _pause_menu.disable()
    _main_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] * → main")


def _back_from_sound():
    _sound_menu.disable()
    if _sound_origin == "pause":
        _pause_menu.enable()
    else:
        _options_menu.enable()


# ── pause actions ─────────────────────────────────────────────────────

def _continue_game():
    global _pause_action
    _pause_action = "CONTINUE"
    _pause_menu.disable()
    if config.debug and config.debug_menu:
        print("[MENU] pause → continue")


def _quit_to_menu():
    global _pause_action
    _pause_action = "QUIT"
    _pause_menu.disable()
    if config.debug and config.debug_menu:
        print("[MENU] pause → quit")


def open_pause_menu():
    _pause_menu.enable()


def get_pause_action():
    return _pause_action


def clear_pause_action():
    global _pause_action
    _pause_action = "NONE"


# ── save / load actions ───────────────────────────────────────────────

def _confirm_new():
    global _next_action
    name = _new_name_input.get_value().strip()
    if not name:
        return
    name = name.replace("/", "_").replace("\\", "_").replace("..", "_")
    config.set_save_name(name)
    os.makedirs(config.SAVE_DIR, exist_ok=True)
    path = os.path.join(config.SAVE_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump({"money": config.STARTING_MONEY, "buildings": []}, f)
    _next_action = "NEW"
    _new_menu.disable()
    if config.debug and config.debug_menu:
        print(f"[MENU] new save created: {name}")


def _select_save(name):
    global _next_action
    config.set_save_name(name)
    _next_action = "LOAD"
    _load_menu.disable()
    if config.debug and config.debug_menu:
        print(f"[MENU] selected save: {name}")


def _show_keybindings():
    print("Keybindings — not implemented yet")


def get_action():
    return _next_action


def clear_action():
    global _next_action
    _next_action = "NONE"


def enable_main_menu():
    _start_menu.disable()
    _new_menu.disable()
    _load_menu.disable()
    _options_menu.disable()
    _sound_menu.disable()
    _pause_menu.disable()
    _main_menu.enable()
    if config.debug and config.debug_menu:
        print("[MENU] enable main menu")


def update_menus(events_list):
    main_was = _main_menu.is_enabled()
    start_was = _start_menu.is_enabled()
    new_was = _new_menu.is_enabled()
    load_was = _load_menu.is_enabled()
    options_was = _options_menu.is_enabled()
    sound_was = _sound_menu.is_enabled()
    pause_was = _pause_menu.is_enabled()
    if main_was:
        _main_menu.update(events_list)
    if start_was:
        _start_menu.update(events_list)
    if new_was:
        _new_menu.update(events_list)
    if load_was:
        _load_menu.update(events_list)
    if options_was:
        _options_menu.update(events_list)
    if sound_was:
        _sound_menu.update(events_list)
    if pause_was:
        _pause_menu.update(events_list)


def draw_menus(surface):
    if _main_menu.is_enabled():
        _main_menu.draw(surface)
    if _start_menu.is_enabled():
        _start_menu.draw(surface)
    if _new_menu.is_enabled():
        _new_menu.draw(surface)
    if _load_menu.is_enabled():
        _load_menu.draw(surface)
    if _options_menu.is_enabled():
        _options_menu.draw(surface)
    if _sound_menu.is_enabled():
        _sound_menu.draw(surface)
    if _pause_menu.is_enabled():
        _pause_menu.draw(surface)
