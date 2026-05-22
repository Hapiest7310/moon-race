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
    ├── level_light.py    ← Light Side (city-builder, buildings, save/load, drop animation)
    └── level_dark.py     ← Dark Side (Asteroids clone with shader-like effects)
```

---

### State Machine

Managed by `App` in `app.py`. Five states:

| State | Entry | Method | What happens |
|-------|-------|--------|-------------|
| `MENU` | Boot | `_update_menu()` | Moon sprite animates, pygame_menu handles navigation |
| `TRANSITION` | New / Load confirmed | `_update_transition()` | Spinner active (2s), then creates LevelLight |
| `PLAYING` | After transition | `_update_playing()` | Delegates to level; ESC → PAUSED. Also handles **minigame** switching (dark side mining) |
| `PAUSED` | ESC in gameplay | `_update_paused()` | Level dims, pause menu overlay; ESC/Continue → PLAYING, Quit → MENU |

When in minigame mode (dark side), `_update_playing` calls `_update_minigame()` instead, which runs LevelDark's loop and auto-exits back to the saved light level when done.

Transitions:
```
MENU → (New/Load) → TRANSITION → (timer) → PLAYING ↔ (ESC) → PAUSED
                                                  ↑               │
                                                  └─── Quit ──────┘
                                                       (ESC/Continue)
                                                       
PLAYING (light) → [Mine button] → minigame (dark) → [ESC/game over] → PLAYING (light, +coins)
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
| `DROP_ANIMATION_MS` | 500 — duration of building placement drop animation |
| `DARK_COUNTDOWN_SECONDS` | 3 — countdown before dark side mining starts |
| `set_save_name(name)` / `get_save_name()` | Mutable current save slot |
| `set_fps(v)` / `get_fps()` | Stores/runs current FPS |
| `set_mine_requested(v)` / `get_mine_requested()` | Flag for light→dark side transition |

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
| `__init__(surface)` | Stores surface + clock, creates moon sprite, initialises spinner, sets up minigame tracking |
| `run()` | Main loop: collect events, dispatch to state method, update spinner, flip display |
| `_update_menu(dt, events)` | Moon animation + menu processing; checks for NEW/LOAD action to start transition |
| `_update_transition(dt, events)` | 2s countdown, then creates LevelLight/LevelDark and starts BGM |
| `_update_playing(dt, events)` | Delegates to level; checks for minigame flag / mine request |
| `_enter_minigame()` | Saves current light level, creates LevelDark(minigame=True), sets minigame flag |
| `_exit_minigame()` | Transfers dark side score as coins to light level, restores saved level |
| `_update_minigame(dt, events)` | Runs LevelDark's loop; auto-exits when `is_minigame_done()` returns True |
| `_update_paused(dt, events)` | Draws level + 128-alpha dim overlay; processes pause menu |

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

Event bleed-through is prevented by caching each menu's enabled state **before** processing any events.

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
| `__init__(surface, save_name)` | Create Grid, BuildingMenu, load from save file, init drop animation state |
| `_is_supported(gx, gy, w, h)` | `True` if gy == 0 or any cell below is occupied |
| `_can_place(gx, gy, w, h)` | Checks money, bounds, overlap, and support |
| `handle_event(event)` | Widget clicks → BuildingMenu; grid click → `_start_drop` for placement animation |
| `update(dt)` | Updates snow, stars, **falling buildings**, particles, hover |
| `draw()` | Fill → stars → buildings → **falling buildings** → **drop particles** → snow → grid → hover → widgets → buttons → money |
| `_start_drop(gx, gy, bt)` | Reserves cells, deducts money, creates drop animation state (duration from `config.DROP_ANIMATION_MS`) |
| `_complete_drop(fb)` | Adds building to `self.buildings`, saves |
| `_compute_drop_offset(progress)` | Exponential ease-out curve for smooth landing |
| `_draw_thrust_flame(fb, offset_y)` | Two-tone flickering rocket flame below descending building |
| `_emit_drop_particles(fb, offset_y)` | Orange/yellow particles shooting downward during descent |
| `_draw_drop_particles()` | Renders particle debris with fade |
| `save()` / `load()` | JSON save/load for buildings + money |

**Building drop animation**: On placement, buildings descend from above the screen with an exponential ease-out curve and a flickering rocket thrust flame. Cells are reserved immediately to prevent overlap. Coins deducted on drop start.

Rendering order:
1. Background fill `(0, 0, 0)`
2. Twinkling star overlay
3. Placed buildings
4. **Falling buildings** (with thrust flame)
5. **Drop particles**
6. Snow overlay
7. Grid lines (debug)
8. Hover preview
9. BuildingMenu widget (top bar)
10. Mode toggle button
11. "Mine Asteroids" button
12. Money text

#### `level_dark.py` — Dark Side (Asteroids clone)

Full Asteroids arcade clone drawn entirely with `pygame.draw.*` shapes.

| Method | Purpose |
|--------|---------|
| `__init__(surface, minigame=False)` | Init game state, countdown, shader layers |
| `handle_event(event)` | Ship controls (arrows + thrust + shoot), minigame exit (ESC / game-over) |
| `update(dt)` | Physics: ship, bullets, asteroids, particles, collisions, wave progression |
| `draw()` | Render to frame buffer: stars → asteroids → bullets → ship → glow → particles → HUD, then blit to screen with shake offset |
| `is_minigame_done()` | Returns `True` when player wants to exit back to light level |
| `get_earnings()` | Returns score (coins earned during mining run) |

**Game objects** (all drawn with `pygame.draw.*`):
- **Ship**: Triangle polygon with rotation, thrust momentum, blink invincibility
- **Asteroids**: Irregular polygons with 3 sizes (large→medium→small), split on destruction
- **Bullets**: Circles with additive glow
- **Particles**: Explosion debris and thrust exhaust (fading circles)

**ShaderSurface class**:
Wraps `pygame.Surface(SRCALPHA)` for blend-mode compositing. Used for:
- Ship glow (BLEND_ADD)
- Bullet glow (BLEND_ADD)
- Particle layer (BLEND_ADD)
- Thrust glow (BLEND_ADD)

Can be swapped for OpenGL framebuffers for real GLSL shader support.

**Effects**:
- Screen shake on collisions (random offset of frame buffer)
- Additive glow layers
- Particle explosions with velocity damping
- Thrust flame + exhaust particles
- Wave announcement text

**Game rules**:
- Start with 3 lives, asteroids per wave = `min(3 + wave, 18)`
- Collisions destroy ship (invincibility blink after respawn)
- Game over → press Enter/Space to return to light level with coins
- ESC during play exits back to light level
- Coins = score (large=20, medium=50, small=100)

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
- **File isolation**: Each save slot is a separate `.json` file.

---

### Pause system

Pressing **ESC** during gameplay transitions to the `PAUSED` state:
1. The level is **still rendered** underneath (no update/handle_event called).
2. A semi-transparent black `Surface` (alpha 128) is blitted over it.
3. The **Pause menu** overlays on top: Continue / Options / Quit.
4. **ESC again** or **Continue** resumes gameplay.
5. **Options** opens the Sound submenu.
6. **Quit** stops BGM, frees the level, returns to Main Menu.

---

### Minigame system (Dark Side mining)

From the Light Side level, clicking the **"Mine Asteroids"** button (top-right HUD) triggers the dark side mining minigame:

1. The App saves the current light level instance
2. Creates `LevelDark(self.surface, minigame=True)`
3. 3-2-1 countdown, then play Asteroids
4. ESC or game-over → exits back to light level
5. All score/coins earned during mining are added to the light level's money
6. Light level BGM continues playing throughout

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
[APP] TRANSITION → PLAYING
[AUDIO] mixer initialized
[AUDIO] registered BGM: 11 -> music/11.mp3
[AUDIO] playing BGM: 11
[BUILD] placed House at (5,0) money=900
[SAVE] saved to saves/mygame.json
[APP] PLAYING → PAUSED (ESC)
[MENU] pause → continue
```

Set `debug = False` in `config.py` to disable all debug output at once.
