# Moon Race — Documentation

## Overview

A 2D pixel-art game built with **Pygame CE** and **pygame_menu** for a university assignment (CT029-3-2 Imaging and Special Effects).  
Three-level moon-themed game: city-builder (Light Side), Asteroids mining (Dark Side), and Alien Evasion (Dark Side 2).

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
├── debug.py              ← DebugManager (named sources, interval-based printing)
├── config.py             ← Constants + debug flags + building types + save name
├── app.py                ← State machine (MENU → TRANSITION → PLAYING / PAUSED)
├── menu.py               ← pygame_menu UI (Main, Start, New, Load, Options, Sound, Pause)
├── sprites.py            ← AnimatedSprite (spritesheet → frames)
├── spinner.py            ← Module-level spinning moon singleton
├── grid.py               ← Bottom-left origin grid (Light Side only)
├── widget/
│   ├── __init__.py       ← Widget base class
│   └── building_menu.py  ← Building type selector with cost display
└── levels/
    ├── __init__.py
    ├── level_base.py     ← Abstract Level interface
    ├── level_light.py    ← Light Side (city-builder, buildings, save/load, drop animation)
    ├── level_dark.py     ← Dark Side (Asteroids clone with shader-like effects)
    └── dark_2/
        └── level_dark2.py ← Alien Evasion minigame
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

When in minigame mode (dark side or alien evasion), `_update_playing` calls `_update_minigame()` instead, which runs the minigame level's loop and auto-exits back to the saved light level when done.

Transitions:
```
MENU → (New/Load) → TRANSITION → (timer) → PLAYING ↔ (ESC) → PAUSED
                                                  ↑               │
                                                  └─── Quit ──────┘
                                                       (ESC/Continue)
                                                        
PLAYING (light) → [Mine button] → asteroids (dark)  → [ESC/game over] → PLAYING (light, +coins)
PLAYING (light) → [Alien button] → alien evasion → [ESC/game over] → PLAYING (light, +coins)
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
| `GROUND_LAYERS` | 6 — layers of procedural ground generated for new saves |
| `CAT_*` | 15+ constants for cat physics, animation, and scale |
| `DARK2_*` | 30+ constants for alien evasion gameplay, moves, and scoring |
| `generate_ground_layers()` | Returns list of Ground tiles for new save files |
| `set_save_name(name)` / `get_save_name()` | Mutable current save slot |
| `set_fps(v)` / `get_fps()` | Stores/runs current FPS |
| `set_mine_requested(v)` / `get_mine_requested()` | Flag for light→dark side transition |
| `set_alien_requested(v)` / `get_alien_requested()` | Flag for light→alien evasion transition |

#### Debug flags

| Flag | Default | Controls |
|------|---------|---------|
| `debug` | False | Master toggle |
| `debug_mouse` | True | Mouse-to-grid coordinate prints |
| `debug_grid` | False | Grid lines + boundary + info text |
| `debug_widgets` | True | Widget debug borders + info |
| `debug_app` | True | State transition prints |
| `debug_spinner` | True | Spinner start/stop prints |
| `debug_hover` | True | Hover cell coordinate label |
| `debug_cells` | True | Cell occupancy debug |
| `debug_layout` | True | Layout bounding rects |
| `debug_menu` | True | Menu navigation prints |
| `debug_audio` | True | Audio init / play / stop prints |
| `debug_cat_state` | True | Cat bounding box + behavior text |
| `debug_cat_manual` | True | Keyboard control for Cat |

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
| `play_music_file(path, loops=-1)` | Load and loop BGM by file path; skips if already playing |
| `stop_music(fade_ms=500)` | Fade out and stop BGM |
| `set_music_volume(vol)` | 0.0–1.0, applied immediately |
| `set_sfx_volume(vol)` | 0.0–1.0, applied to all cached SFX |
| `get_music_volume()` / `get_sfx_volume()` | Current volume levels |

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
| `_enter_minigame()` | Saves current light level, creates LevelDark (asteroids) |
| `_enter_alien_minigame()` | Saves current light level, creates LevelDark2 (alien evasion) |
| `_exit_minigame()` | Transfers minigame score as coins to saved light level, restores it |
| `_update_minigame(dt, events)` | Runs minigame level loop; auto-exits when `is_minigame_done()` returns True |
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

#### `level_dark2.py` — Dark Side 2 (Alien Evasion)

Top-down dodge-em-up with AI-driven enemies. Drawn entirely with `pygame.draw.*` shapes.

| Method | Purpose |
|--------|---------|
| `__init__(surface, minigame=False, dm=None)` | Init game state, countdown, starfield, particle/shake systems |
| `_init_game()` | Reset score, lives, enemies, timers for a new round |
| `_spawn_enemy()` | Place enemy at random position ≥ `DARK2_SPAWN_MARGIN` from edges, ≥ `DARK2_SPAWN_MIN_PLAYER_DIST` from player |
| `_predict_player_pos()` | Estimate future player position from movement history bias |
| `handle_event(event)` | ESC to exit, any key after game over to return |
| `update(dt)` | Score accumulation, player movement, enemy AI, bullet updates, collisions |
| `draw()` | Stars → enemies → bullets → particles → player → glow → HUD (score + lives) → screen shake |
| `_check_collisions()` | Distance-based hit test vs enemies and bullets |
| `_on_player_hit()` | Decrement lives; at 0 → game over, else clear enemies + blink |
| `is_minigame_done()` | Returns `True` when ESC pressed or key hit after game over |

**Enemy AI moves** (selected probabilistically each frame):
- **Dash**: Wind up, then fast linear dash toward predicted player position
- **Shoot**: Wind up, fire spread of bullets toward player
- **Explode**: Blink, then detonate in a radial bullet burst
- **Attract**: Pair with another enemy, accelerate toward each other, merge-explode on contact

**Game rules**:
- 3 lives (`DARK2_PLAYER_LIVES`), lost on enemy/bullet collision
- Score = `floor(elapsed_seconds) * DARK2_COINS_PER_SECOND` (10/sec)
- No time limit — game only ends when all lives are lost
- Difficulty ramps: enemy speed multiplier increases over time
- Enemies grow larger if player avoids them too long

**Config constants** (all prefixed `DARK2_`):

| Constant | Value | Purpose |
|----------|-------|---------|
| `PLAYER_RADIUS` | 20 | Player collision radius |
| `PLAYER_ACCEL` | 1600.0 | Player acceleration (px/s²) |
| `PLAYER_MAX_SPEED` | 200.0 | Player speed cap |
| `PLAYER_FRICTION` | 0.85 | Velocity damping per frame |
| `ENEMY_RADIUS` | 10 | Base enemy radius |
| `ENEMY_BASE_SPEED` | 90.0 | Base enemy chase speed |
| `ENEMY_SPAWN_INTERVAL` | 5000 | ms between new enemy spawns |
| `ENEMY_GROW_INTERVAL` | 10000 | ms without hit before enemies grow |
| `ENEMY_GROW_MAX_RADIUS` | 20 | Max enemy size from growth |
| `DIFFICULTY_RATE` | 0.15 | Speed multiplier increase per 60s |
| `DIFFICULTY_MAX_MULTIPLIER` | 3.0 | Max difficulty scaling |
| `COINS_PER_SECOND` | 10 | Score earned per second survived |
| `PLAYER_LIVES` | 3 | Hits before game over |
| `BLINK_DURATION` | 500 | ms invulnerability after hit |
| `SPAWN_MARGIN` | 80 | Min px from screen edge for spawn |
| `SPAWN_MIN_PLAYER_DIST` | 200 | Min px from player for spawn |
| `PREDICT_OFFSET` | 200.0 | Look-ahead px for player prediction |
| `STAR_COUNT` | 160 | StarField particle count |
| `SHAKE_HIT` | 4 | Screen shake intensity on hit |

Move-specific constants (`DARK2_MOVE_DASH_*`, `DARK2_MOVE_SHOOT_*`, etc.) control each AI move's chance, cooldown, and parameters.

---

### Minigame system (Dark Side mining & Alien Evasion)

Two minigames are accessible from the Light Side level via HUD buttons (top-right):

**Mine Asteroids** (`LevelDark`):
1. App saves the current light level instance
2. Creates `LevelDark(self.surface, minigame=True)`
3. 3-2-1 countdown, then play Asteroids (60s time limit)
4. ESC or game-over → exits back to light level
5. Score (asteroid destruction) added as coins to light level money

**Alien Evasion** (`LevelDark2`):
1. App saves the current light level instance
2. Creates `LevelDark2(self.surface, minigame=True)`
3. 3-2-1 countdown, then dodge enemies endlessly
4. Game ends only when all 3 lives are lost
5. Coins = `floor(seconds_survived) * 10`
6. ESC to exit early (no coins)

Both restore the light level and its BGM on exit.

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
