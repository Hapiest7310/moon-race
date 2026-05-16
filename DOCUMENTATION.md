# Moon Race — Documentation

## Overview

A 2D pixel-art game built with **Pygame CE** and **pygame_menu** for a university assignment (CT029-3-2 Imaging and Special Effects).  
Two-level moon-themed game with a city-builder (Light Side) and an Asteroids-mining (Dark Side) level.

**Resolution:** 1920×1080 fullscreen  
**Framerate:** 60 FPS  
**Language:** Python 3.14  

---

## Architecture

```
main.py                   ← Entry point (init, fullscreen, launch App)
music/
└── 11.mp3                ← Background music track
src/
├── audio.py              ← Audio manager (BGM + SFX, volume control)
├── config.py             ← Constants + debug flags + building types + save name
├── app.py                ← State machine (MENU → TRANSITION → PLAYING / PAUSED)
├── menu.py               ← pygame_menu UI (Main, Start, New, Load, Options, Sound, Pause)
├── sprites.py            ← AnimatedSprite (spritesheet → frames)
├── spinner.py            ← Module-level spinning moon singleton
├── grid.py               ← Bottom-left origin grid (Light Side only)
├── widget/
│   ├── __init__.py       ← Widget base class
│   ├── color_picker.py   ← 8-color picker widget (legacy)
│   └── building_menu.py  ← Building type selector with cost display
└── levels/
    ├── __init__.py
    ├── level_base.py     ← Abstract Level interface
    ├── level_light.py    ← Light Side (city-builder, buildings, save/load)
    └── level_dark.py     ← Dark Side stub (Asteroids-style)
```

---

### State Machine

Managed by `App` in `app.py`. Four states:

| State | Entry | Method | What happens |
|-------|-------|--------|-------------|
| `MENU` | Boot | `_update_menu()` | Moon sprite animates, pygame_menu handles navigation |
| `TRANSITION` | New / Load confirmed | `_update_transition()` | Spinner active (2s), then creates LevelLight |
| `PLAYING` | After transition | `_update_playing()` | Delegates `handle_event` / `update` / `draw` to level; ESC → PAUSED |
| `PAUSED` | ESC in gameplay | `_update_paused()` | Level dims, pause menu overlay; ESC/Continue → PLAYING, Quit → MENU |

Transitions:
```
MENU → (New/Load) → TRANSITION → (timer) → PLAYING ↔ (ESC) → PAUSED
                                                 ↑               │
                                                 └─── Quit ──────┘
                                                      (ESC/Continue)
```

---

## File-by-File Reference

### `main.py` — Entry point

| Function | Purpose |
|----------|---------|
| `main()` | Init pygame, init audio mixer + load tracks, open fullscreen window, create menus, launch `App` |

Audio initialisation (`audio.init()`, `audio.load_all()`) happens before the display surface is created, so BGM tracks are ready when the game starts.

---

### `src/config.py` — Central configuration

| Constant / Function | Value / Purpose |
|---------------------|-----------------|
| `SCREEN_WIDTH` / `SCREEN_HEIGHT` | 1920 / 1080 |
| `GRID_CELL_SIZE` | 32 |
| `STARTING_MONEY` | 1000 |
| `SAVE_DIR` | `"saves"` |
| `BUILDING_TYPES` | 8 building definitions: name, w, h, cost, color |
| `MUSIC_DIR` | `"music"` |
| `AUDIO_ENABLED` | Master audio toggle |
| `DEFAULT_MUSIC_VOLUME` / `DEFAULT_SFX_VOLUME` | 0.5 / 0.7 |
| `set_save_name(name)` / `get_save_name()` | Mutable current save slot |
| `set_fps(v)` / `get_fps()` | Stores/runs current FPS |

#### Debug flags

| Flag | Default | Controls |
|------|---------|---------|
| `debug` | True | Master toggle |
| `debug_mouse` | True | Mouse-to-grid coordinate prints |
| `debug_grid` | True | Grid lines + boundary + info text |
| `debug_widgets` | True | Widget debug borders + info |
| `debug_app` | True | State transition prints |
| `debug_spinner` | True | Spinner start/stop prints |
| `debug_hover` | True | Hover cell coordinate label |
| `debug_layout` | True | Layout bounding rects |
| `debug_menu` | True | Menu navigation prints |
| `debug_audio` | True | Audio init / play / stop prints |

#### Building types

| Name | Size | Cost | Color |
|------|------|------|-------|
| Foundation | 1×1 | 10 | Brown |
| Wall | 2×1 | 50 | Grey |
| Tower | 1×2 | 50 | Dark blue-grey |
| House | 2×2 | 100 | Sienna |
| Workshop | 3×2 | 200 | Tan |
| Mansion | 3×3 | 300 | Cornflower blue |
| Palace | 4×4 | 500 | Goldenrod |
| Observatory | 2×4 | 400 | Medium purple |

---

### `src/audio.py` — Audio manager

Module-level singleton (same pattern as `spinner.py`). Any module can call `audio.play_music("11")` without a reference.

| Function | Purpose |
|----------|---------|
| `init()` | `pygame.mixer.init()` with 44.1kHz/16-bit/stereo; no-op if already inited or `AUDIO_ENABLED` is False |
| `load_all()` | Scan `MUSIC_DIR` for `.mp3`/`.ogg`/`.wav` files, register by filename stem |
| `play_music(name, loops=-1)` | Load and loop BGM track by stem name; skips if already playing |
| `stop_music(fade_ms=500)` | Fade out and stop BGM |
| `set_music_volume(vol)` | 0.0–1.0, applied immediately |
| `set_sfx_volume(vol)` | 0.0–1.0, applied to all cached SFX |
| `load_sfx(name, path)` | Load a `pygame.mixer.Sound` by name |
| `play_sfx(name)` | Play one-shot SFX |
| `get_music_volume()` / `get_sfx_volume()` | Current volume levels |
| `is_playing()` | `True` if mixer is active and music is playing |

All functions are safe to call even if `AUDIO_ENABLED = False` or `mixer.init()` failed — they silently no-op and log with `debug_audio`.

---

### `src/app.py` — Application state machine

| Method | Purpose |
|--------|---------|
| `__init__(surface)` | Stores surface + clock, creates moon sprite, initialises spinner |
| `run()` | Main loop: collect events, dispatch to state method, update spinner, flip display |
| `_update_menu(dt, events)` | Moon animation + menu processing; checks for NEW/LOAD action to start transition |
| `_update_transition(dt, events)` | 2s countdown, then creates `LevelLight(surface, save_name)` and starts BGM |
| `_update_playing(dt, events)` | Delegates to level's handle/update/draw; ESC → open pause menu, state = PAUSED |
| `_update_paused(dt, events)` | Draws level + 128-alpha dim overlay; processes pause menu; ESC/Continue → PLAYING, Quit → MENU |

Key design: `App` does NOT know what the level does internally — it calls the `Level` interface methods.

---

### `src/menu.py` — pygame_menu navigation

Seven menus, only one enabled at a time:

```
Main Menu
├── Start    → disables main, enables start_menu
├── Options  → disables main, enables options_menu
└── Quit     → pygame_menu events.EXIT

Start Submenu
├── New Game  → opens New Game submenu (text input)
├── Load Game → opens Load Game submenu (file listing)
└── Back      → re-enables main_menu

New Game Submenu
├── [text input "Save name:"]  ← type a name
├── Confirm  → creates saves/<name>.json, sets action = NEW
└── Back     → re-enables start_menu

Load Game Submenu
├── [dynamic buttons, one per .json in saves/]
│   └── click → sets save name, action = LOAD
└── Back     → re-enables start_menu

Options Submenu
├── Keybindings → print stub
├── Sound       → opens Sound submenu
└── Back        → re-enables main_menu

Sound Submenu
├── Music Volume range slider (0–100)
├── SFX Volume  range slider (0–100)
└── Back        → returns to caller (Options or Pause)

Pause Submenu (opened by ESC during gameplay)
├── Continue → resumes game (state = PLAYING)
├── Options  → opens Sound submenu (Back returns to Pause)
└── Quit     → stops music, frees level, returns to main menu
```

| Functions | Purpose |
|-----------|---------|
| `create_menus()` | Build all 7 menus with callbacks |
| `get_main_menu()` | Return main menu reference |
| `get_action()` / `clear_action()` | App queries NEW/LOAD transition trigger |
| `get_pause_action()` / `clear_pause_action()` | App queries CONTINUE/QUIT pause action |
| `open_pause_menu()` | Enable pause menu (called by App on ESC) |
| `enable_main_menu()` | Disable all, enable main (on ESC Quit) |
| `update_menus(events)` | Snapshot enabled states before processing to prevent event bleed-through |
| `draw_menus(surface)` | Draw all enabled menus |

Event bleed-through is prevented by caching each menu's enabled state **before** processing any events. This ensures a menu enabled during another menu's event callback does not receive the same frame's remaining events.

---

### `src/sprites.py` — AnimatedSprite

| Method | Purpose |
|--------|---------|
| `__init__(x, y, path, fw, fh, count, speed, scale)` | Load spritesheet, slice into frames |
| `load_frames(count, scale)` | Extract frame rects from horizontal spritesheet |
| `set_position(pos)` | Move sprite center |
| `update(dt)` | Advance frame, loop at `animation_speed` interval |

Uses `pygame.Surface.subsurface()` to slice without copying pixel data.

---

### `src/spinner.py` — Module-level loading spinner

Module-level singleton. Any code can call `spinner.start()` / `spinner.stop()`.

| Function | Purpose |
|----------|---------|
| `init()` | Create spinning moon `AnimatedSprite` (60ms) + font |
| `start(caption)` | Activate spinner with text |
| `stop()` | Deactivate |
| `is_active()` | Returns active state |
| `update(dt)` | Advance moon animation |
| `draw(surface)` | Fill dark, draw spinning moon centered, draw caption below |

Non-blocking — renders in the App's main loop each frame.

---

### `src/grid.py` — Bottom-left origin grid

Coordinate system with (0, 0) at the **bottom-left**. Y-axis increases upward.

| Method | Purpose |
|--------|---------|
| `__init__()` | Read cell_size, cols, rows from config |
| `grid_to_pixel(gx, gy)` | `px = gx * cs`, `py = HEIGHT - (gy + 1) * cs` |
| `pixel_to_grid(px, py)` | Inverse: `gx = px // cs`, `gy = (HEIGHT - py - 1) // cs` |
| `is_in_bounds(gx, gy)` | `0 ≤ gx < cols` and `0 ≤ gy < rows` |
| `draw(surface)` | Debug grid lines + boundary rect + info text (gated by `debug_grid`) |

Grid: 60 cols × 33 rows × 32px = 1920 × 1056 px, 24px unused at screen top.

---

### `src/widget/` — Widget system

#### `__init__.py` — Widget base class

| Method | Purpose |
|--------|---------|
| `__init__(rect)` | Store `pygame.Rect` (absolute) |
| `handle_event(event)` | Override in subclass; return `True` if consumed |
| `update(dt)` | Per-frame logic |
| `draw(surface)` | Render widget |
| `get_debug_info()` | `"[WIDGET] ClassName — rect=(x, y, w, h)"` |

All internal widget coordinates are **local** relative to `self.rect`.

#### `color_picker.py` — 8-color palette (legacy, unused in current level)

| Method | Purpose |
|--------|---------|
| `COLORS` | 8 preset RGB tuples |
| `_build_buttons()` | Create 8 button rects, centred |
| `get_selected_color()` | Return RGB of selected button |
| `handle_event(event)` | Local-coordinate button hit testing |
| `draw(surface)` | Coloured squares; selected has white 3px border |

#### `building_menu.py` — Building type selector

| Method | Purpose |
|--------|---------|
| `__init__(rect)` | Creates buttons proportional to building size |
| `get_selected_building()` | Return currently selected `BUILDING_TYPES` dict |
| `_build_buttons()` | Compute button rects from building w/h |
| `handle_event(event)` | Local-coordinate click → select building type |
| `draw(surface)` | Draw coloured rects with `W×H` label + cost text below |

The menu auto-adjusts button sizes to visually represent the building's footprint.  
Cost text is drawn **white** if `self.money ≥ cost`, **red** otherwise.

---

### `src/levels/` — Level system

#### `level_base.py` — Abstract interface

| Method | Purpose |
|--------|---------|
| `__init__(surface)` | Store surface, set `done = False` |
| `handle_event(event)` | Process pygame events |
| `update(dt)` | Per-frame logic |
| `draw()` | Render everything to `self.surface` |
| `get_debug_info()` | Returns `"[LEVEL] ClassName"` |

#### `level_light.py` — Light Side (city-builder)

| Method | Purpose |
|--------|---------|
| `__init__(surface, save_name)` | Create Grid, BuildingMenu (top, full-width), load from save file |
| `_is_supported(gx, gy, w, h)` | `True` if gy == 0 (ground) or any cell below is occupied |
| `_can_place(gx, gy, w, h)` | Checks money, bounds, overlap, and support |
| `handle_event(event)` | Widget clicks → BuildingMenu; grid click → place selected building if valid |
| `update(dt)` | Sync money to widget, track hover cell |
| `draw()` | Fill → draw buildings → grid → hover preview → BuildingMenu → money HUD |
| `_draw_buildings()` | Iterate `self.buildings`, render each cell by building colour |
| `_draw_hover()` | Green/red highlight at building footprint; shows `(gx,gy) OK/NO` in debug |
| `_draw_money()` | `$ N` gold text at top-right |
| `save()` | Write JSON to `saves/{save_name}.json` (money + building list) |
| `load()` | Read JSON, restore buildings and `_occupied_cells` set |

Rendering order:
1. Background fill `(20, 25, 40)`
2. Placed buildings (coloured cells)
3. Grid lines + boundary (debug)
4. Hover preview (green/red overlay)
5. BuildingMenu widget (top bar)
6. Money text (top-right)

#### Placement rules

- **Support**: Building must be on ground (`gy == 0`) or at least one cell of its bottom row must rest on an occupied cell.
- **Overlap**: Cannot place over existing buildings or out of bounds.
- **Cost**: Deducted from `self.money` on placement. Checked beforehand in `_can_place`.
- **Save**: Auto-saves to `saves/{save_name}.json` after every placement. Loaded on level init.

#### `level_dark.py` — Dark Side stub

Minimal fill with `(10, 10, 20)` background. Ready for Asteroids-style implementation.

---

### Save / Load system

Save files are JSON in `saves/` directory:

```json
{
  "money": 850,
  "buildings": [
    {"type": "House", "gx": 5, "gy": 0},
    {"type": "Tower", "gx": 7, "gy": 1}
  ]
}
```

- **New Game**: User enters a name → creates `saves/<name>.json` with 1000 money and empty buildings.
- **Load Game**: Lists all `.json` files in `saves/`; selecting one restores money and all placed buildings.
- **Auto-save**: Every building placement triggers `save()`.
- **File isolation**: Each save slot is a separate `.json` file. Switching saves preserves independent game states.

---

### Pause system

Pressing **ESC** during gameplay transitions to the `PAUSED` state:
1. The level is **still rendered** underneath (no update/handle_event called).
2. A semi-transparent black `Surface` (alpha 128) is blitted over it.
3. The **Pause menu** overlays on top: Continue / Options / Quit.
4. **ESC again** or **Continue** resumes gameplay.
5. **Options** opens the Sound submenu (volume sliders); Back returns to Pause.
6. **Quit** stops BGM, frees the level, returns to Main Menu.

---

### Audio system

- **BGM**: `11.mp3` plays on loop when Light Side level loads. Stops on ESC Quit.
- **Mixer**: Initialised in `audio.init()` at 44.1kHz, 16-bit, stereo, 512-byte buffer.
- **Volume**: Two independent channels (Music / SFX), each 0.0–1.0, adjustable via Sound submenu sliders.
- **Graceful degradation**: If `AUDIO_ENABLED = False` or `mixer.init()` fails, all audio functions silently no-op.

---

## Debug Output Format

All debug output uses `[TAG]` prefix:

```
[MENU] main → start
[MENU] action set: LOAD
[APP] MENU → TRANSITION (LOAD)
[SPINNER] start "Loading game..."
[SPINNER] stop
[APP] TRANSITION → PLAYING (Light Side)
[AUDIO] mixer initialized
[AUDIO] registered BGM: 11 -> music/11.mp3
[AUDIO] playing BGM: 11
[BUILD] placed House at (5,0) money=900
[SAVE] saved to saves/mygame.json
[APP] PLAYING → PAUSED (ESC)
[MENU] pause → continue
```

Set `debug = False` in `config.py` to disable all debug output at once.
