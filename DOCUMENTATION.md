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
src/
├── config.py             ← Constants + debug flags + FPS accessor
├── app.py                ← State machine (MENU → TRANSITION → PLAYING)
├── menu.py               ← pygame_menu UI (Start, Options, Quit)
├── sprites.py            ← AnimatedSprite (spritesheet → frames)
├── spinner.py            ← Module-level spinning moon singleton
├── grid.py               ← Bottom-left origin grid (Light Side only)
├── widget/
│   ├── __init__.py       ← Widget base class
│   └── color_picker.py   ← 8-color picker widget
└── levels/
    ├── __init__.py
    ├── level_base.py     ← Abstract Level interface
    ├── level_light.py    ← Light Side (city-builder, grid, paint)
    └── level_dark.py     ← Dark Side stub (Asteroids-style)
```

### State Machine

Managed by `App` in `app.py`. Three states, each a separate method:

| State | Entry | Method | What happens |
|-------|-------|--------|-------------|
| `MENU` | Boot | `_update_menu()` | Moon sprite animates in background, pygame_menu handles navigation |
| `TRANSITION` | Click Load/New | `_update_transition()` | Spinner active (timer-based, 2s), then creates Level instance |
| `PLAYING` | After transition | `_update_playing()` | Delegates to `level.handle_event()`, `.update()`, `.draw()` |

Transitions:
```
MENU → (Load/New) → TRANSITION → (timer) → PLAYING → (ESC) → MENU
```

---

## File-by-File Reference

### `main.py` — Entry point

| Function | Purpose |
|----------|---------|
| `main()` | Init pygame, open fullscreen 1920×1080 window, create menus, launch `App`, quit on exit |

Only 3 responsibilities: init, window, launch.

---

### `src/config.py` — Central configuration

| Constant | Value | Purpose |
|----------|-------|---------|
| `SCREEN_WIDTH` / `SCREEN_HEIGHT` | 1920 / 1080 | Display resolution |
| `GRID_CELL_SIZE` | 32 | Pixel size of one grid cell |
| `GRID_COLS` | `SCREEN_WIDTH // 32 → 60` | Auto-calculated |
| `GRID_ROWS` | `SCREEN_HEIGHT // 32 → 33` | Auto-calculated |
| `debug` | True | Master toggle — disables all debug when False |

| Debug flag | Default | Controls |
|-----------|---------|---------|
| `debug_mouse` | True | Pixel → grid coordinate terminal output |
| `debug_grid` | True | Grid lines + boundary rect + info text |
| `debug_widgets` | True | Green border around widget rects + debug info in overlay |
| `debug_fps` | True | FPS counter in overlay HUD |
| `debug_app` | True | App state transition prints |
| `debug_spinner` | True | Spinner start/stop prints |
| `debug_hover` | True | Cell coordinate label on hovered cell |
| `debug_cells` | True | Painted cell count in overlay |
| `debug_layout` | True | Colored bounding rects (yellow=overlay, blue=grid, green=widget) |
| `debug_menu` | True | Menu navigation prints |

| Function | Purpose |
|----------|---------|
| `set_fps(v)` | Called by App each frame to store current FPS |
| `get_fps()` | Read by LevelLight for overlay display |
| `get_screen_center()` | Returns `(960, 540)` |
| `get_moon_position()` | Returns center-adjusted position for menu moon sprite |

---

### `src/app.py` — Application state machine

| Method | Purpose |
|--------|---------|
| `__init__(surface)` | Stores surface + clock, creates moon sprite, initializes spinner |
| `run()` | Main loop: collects events, dispatches to state method, updates spinner, flips display |
| `_update_menu(dt, events)` | Updates moon animation, processes menus, checks for LOAD/NEW action |
| `_update_transition(dt, events)` | Decrements timer, on expiry stops spinner and creates `LevelLight` |
| `_update_playing(dt, events)` | Delegates `handle_event` / `update` / `draw` to current level instance; ESC returns to menu |

Key design: The `App` does NOT know what the level does internally. It just calls the three methods on the `Level` interface. This makes adding new levels trivial.

---

### `src/menu.py` — pygame_menu navigation

Three menus, only one enabled at a time:

```
Main Menu
├── Start    → disables main, enables start_menu
├── Options  → disables main, enables options_menu
└── Quit     → pygame_menu events.EXIT

Start Submenu
├── Load     → sets _next_action = "LOAD", disables start
├── New      → sets _next_action = "NEW", disables start
└── Back     → re-enables main_menu

Options Submenu
├── Keybindings → print stub
├── Sound       → print stub
└── Back        → re-enables main_menu
```

| Functions | Purpose |
|-----------|---------|
| `create_menus()` | Build all 3 menus with button callbacks |
| `get_main_menu()` | Return main menu reference (for initial enable) |
| `get_action()` / `clear_action()` | App queries whether user clicked Load or New |
| `enable_main_menu()` | Reactivate main menu (after ESC from gameplay) |
| `update_menus(events)` / `draw_menus(surface)` | Forward pygame events / draw calls to the active menu |

All private callbacks (`_open_start`, `_set_load`, `_back_to_main`, etc.) handle menu enable/disable transitions AND print debug when `debug_menu` is on.

---

### `src/sprites.py` — AnimatedSprite

| Method | Purpose |
|--------|---------|
| `__init__(x, y, sprite_sheet_path, frame_width, frame_height, frame_count, animation_speed, scale)` | Load spritesheet, slice into frames, set initial position |
| `load_frames(frame_count, scale)` | Extract each frame rect from horizontal spritesheet, optionally scale |
| `set_position(position)` | Move sprite center to new (x, y) |
| `update(dt)` | Advance frame based on elapsed ms (`dt`), loop at `animation_speed` interval |

Uses `pygame.Surface.subsurface()` to slice frames from the spritesheet without copying pixel data.

---

### `src/spinner.py` — Module-level loading spinner

Module-level singleton (no class). Any code can call `spinner.start()` / `spinner.stop()` without needing a reference.

| Function | Purpose |
|---------|---------|
| `init()` | Create the `AnimatedSprite` moon (fast 60ms animation) + font |
| `start(caption)` | Set `_active = True`, store caption text |
| `stop()` | Set `_active = False` |
| `is_active()` | Return active state (checked by App in main loop) |
| `update(dt)` | Advance moon animation frame |
| `draw(surface)` | Fill screen dark, draw spinning moon centered, draw caption text below |

The spinner does NOT block the game loop. It renders in the App's main loop each frame, so the rest of the app can keep processing. The App simply calls `spinner.start()` before the transition timer and `spinner.stop()` after.

---

### `src/grid.py` — Bottom-left origin grid

Coordinate system with (0, 0) at the **bottom-left** of the screen. Y-axis increases upward (opposite of pygame's native top-down).

| Method | Purpose |
|--------|---------|
| `__init__()` | Read config for cell_size, cols, rows |
| `grid_to_pixel(gx, gy)` | Grid → screen pixel: `px = gx * cell_size`, `py = SCREEN_HEIGHT - (gy + 1) * cell_size` |
| `pixel_to_grid(px, py)` | Pixel → grid: `gx = px // cell_size`, `gy = (SCREEN_HEIGHT - py - 1) // cell_size` |
| `is_in_bounds(gx, gy)` | Bounds check: `0 ≤ gx < cols` and `0 ≤ gy < rows` |
| `draw(surface)` | When `debug_grid`: draw horizontal lines bottom-up (y=1080, 1048, …, 24), vertical lines clipped to grid area. Blue boundary rect + info text at screen bottom |

Grid area: 60 columns × 33 rows × 32px = 1920 × 1056 pixels, with 24px uncovered at the top (1080 - 33×32 = 24).

---

### `src/widget/` — Widget system

#### `__init__.py` — Widget base class

| Method | Purpose |
|--------|---------|
| `__init__(rect)` | Store `pygame.Rect` (absolute screen position) |
| `handle_event(event)` | Override in subclass. Return `True` if event was consumed |
| `update(dt)` | Per-frame logic |
| `draw(surface)` | Render widget |
| `get_debug_info()` | Returns `"[WIDGET] ClassName — rect=(x, y, w, h)"` |

All internal widget coordinates are **local** relative to `self.rect`. Convert to absolute only when drawing via `btn.move(self.rect.x, self.rect.y)`.

#### `color_picker.py` — 8-color palette

| Attribute / Method | Purpose |
|--------------------|---------|
| `COLORS` | 8 preset RGB tuples: red, orange, yellow, green, cyan, blue, purple, white |
| `_build_buttons()` | Create 8 local `pygame.Rect` button regions, centered within widget width |
| `get_selected_color()` | Return RGB of currently selected button |
| `handle_event(event)` | Check if click is within widget → convert to local coords → check each button rect |
| `draw(surface)` | Draw 8 colored squares; selected gets white border (3px), others get grey border (1px) |
| `get_debug_info()` | Adds `selected=N color=(R,G,B)` |

---

### `src/levels/` — Level system

#### `level_base.py` — Abstract interface

| Method | Purpose |
|--------|---------|
| `__init__(surface)` | Store display surface, set `done = False` |
| `handle_event(event)` | Process pygame events (mouse clicks, keyboard) |
| `update(dt)` | Per-frame logic with delta time |
| `draw()` | Render everything to `self.surface` |
| `get_debug_info()` | Returns `"[LEVEL] ClassName"` |

#### `level_light.py` — Light Side (city-builder)

| Method | Purpose |
|--------|---------|
| `__init__(surface)` | Create `Grid`, `ColorPicker` widget (bottom-left), `pygame_menu` overlay (top-left, 520×170, 6 label lines), hover surface |
| `_is_over_widget(pos)` | Check if mouse is over any widget rect or overlay rect |
| `handle_event(event)` | Widgets get first chance → if over widget region skip → otherwise paint grid cell |
| `update(dt)` | Track hover cell (skip if over widget); mouse debug print on cell change |
| `draw()` | Fill bg → draw painted cells → draw grid → draw hover → draw widgets (+ debug borders) → draw overlay |
| `_draw_painted_cells()` | Iterate `self.cell_colors` dict, draw each colored cell rect |
| `_draw_hover()` | SRCALPHA white highlight on hovered cell + optional coordinate label |
| `_draw_layout_overlay()` | Colored rects: blue=grid, green=widget, yellow=overlay |
| `_draw_overlay()` | Build 6-line string from active debug flags, update pygame_menu labels, draw via subsurface |
| `get_debug_info()` | Returns level name + painted cell count |

Rendering order (back to front):

1. Background fill `(20, 25, 40)`
2. Painted cells (colored rects)
3. Grid lines + boundary (debug)
4. Hover highlight + label
5. Widgets (color picker) + debug borders
6. Layout debug rects
7. Overlay HUD (pygame_menu via subsurface)

#### `level_dark.py` — Dark Side stub

Minimal fill with `(10, 10, 20)` background. No grid, no widgets. Ready for Asteroids-style implementation.

---

### Overlay HUD (6-line debug panel)

Position: `(10, 10)`, size `520×170`, rendered via `surface.subsurface()`.  
Uses `pygame_menu.Menu` with 6 left-aligned label widgets.

| Line | Content | Gated by |
|------|---------|----------|
| 0 | `FPS: 60  \|  state: PLAYING  level: Light Side` | `debug_fps` + `debug_app` |
| 1 | `pixel: (373, 267)  grid: (11, 25)` | `debug_mouse` |
| 2 | `hover: (12, 8)` or `hover: ---` | `debug_hover` |
| 3 | `ColorPicker: selected=0 color=(255,50,50)` | `debug_widgets` |
| 4 | `painted cells: 42` | `debug_cells` |
| 5 | `grid: 60c x 33r` | Always on with `debug` |

---

### Layer Interaction System

The level separates two interaction layers:

| Layer | What renders | What receives events | Checked by |
|-------|-------------|---------------------|------------|
| **Widget** | Color picker + overlay HUD | Color picker clicks, overlay is non-interactive | `_is_over_widget(pos)` |
| **Grid** | Background, painted cells, grid lines, hover | Cell painting clicks + hover tracking | After widget check returns `False` |

The `_is_over_widget(pos)` method checks all visible widget rects AND the overlay rect. If `True`:
- Hover highlight is cleared (no grid cell highlighted behind a widget)
- Click passes through to widget first; if unhandled, it's still consumed (no grid paint)

---

## Debug Output Format

All debug output uses `[TAG]` prefix for easy filtering:

```
[MENU] main → start
[MENU] action set: LOAD
[APP] MENU → TRANSITION (LOAD)
[SPINNER] start "Loading game..."
[SPINNER] stop
[APP] TRANSITION → PLAYING (Light Side)
[MOUSE] pixel (373, 267) -> grid (11, 25)
[PAINT] cell (12, 8) -> (255, 50, 50)  total=1
```

Set `debug = False` in `config.py` to disable all debug output at once.
