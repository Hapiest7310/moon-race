# Moon Race — Game Report

## 1. Introduction

Moon Race is a 2D colony-building game built with Pygame. The player takes on the role of an astronaut tasked with constructing a functional moon base by placing buildings on a grid. Resources are gathered through two minigames: mining asteroids (Dark Side 1) and evading alien attacks (Dark Side 2). A unique feature is the presence of an AI-controlled space cat that roams the player's structures autonomously, reacting to the environment with animated behaviours. The game combines construction simulation, resource management, and arcade-style action sequences within a single cohesive experience.

## 2. Storyboard Narrative

The player is an astronaut who must build a self-sufficient colony on the Moon. Materials are acquired by venturing into asteroid fields to mine resources. Occasionally, alien threats appear and must be evaded to protect the colony. Along the way, the player can adopt and care for a space cat that explores the base. The narrative unfolds through the gameplay loop: build structures on the light side, mine for resources on the dark side, and defend against alien incursions.

### Key Story Beats
1. Player lands on the Moon with basic resources and a empty grid.
2. Foundation structures are placed to establish the colony.
3. Asteroid mining minigame unlocks — player pilots a ship to collect ore.
4. Alien evasion minigame unlocks — player dodges hostile enemies.
5. Earnings from minigames fund larger buildings (Workshop, Mansion, Palace, Observatory).
6. The space cat arrives and roams the completed base.

## 3. Game Scene & Assets

### 3.1 Screenshots

*[Screenshot of the light-side base-building level with grid, placed buildings, cat, and HUD]*

*[Screenshot of the asteroid mining minigame (Dark Side 1) with ship, asteroids, and score]*

*[Screenshot of the alien evasion minigame (Dark Side 2) with player, enemies, bullets, and lives]*

### 3.2 Asset Explanations

| Asset | Source | Description |
|-------|--------|-------------|
| Buildings spritesheet (`Buildings.png`) | External asset | Spritesheet containing all building tiles (Foundation, Wall, Tower, House, Workshop, Mansion, Palace, Observatory, green_house). Each building is cropped from the spritesheet during loading. |
| Cat sprite animations | External asset | Frame-based PNG sequences in `assets/images/cat/` directory (idle_1, idle_2, hiss, lick_1, lick_2, sleep, jump, run_1, run_2). Loaded and scaled by `Cat._load_animations()`. |
| Ground tiles | Programmatic | White 1×1 grid cells rendered as filled rectangles — no spritesheet needed. |
| Star background | Programmatic + ShaderSurface | 200 twinkling stars rendered via `ShaderSurface` with additive blending (`BLEND_ADD`) and parallax horizontal drift. |
| Snow overlay | Programmatic | 120 semi-transparent white particles falling at varying speeds with sinusoidal horizontal sway. |
| Grid | Programmatic | 60×33 cell grid (32px cells) drawn as lines when debug enabled. |

## 4. Visual & Audio Special Effects

### 4.1 Visual Effects

- **Star field parallax**: Stars drift horizontally at different speeds creating depth. Twinkle effect achieved by cycling alpha values. Rendered on a `ShaderSurface` with `BLEND_ADD` for a glowing appearance.
- **Snow overlay**: 120 particles with randomised size (1–3px), speed, and horizontal oscillation (`sin(time + offset)`). Semi-transparent surface (alpha 51) drawn over the scene.
- **Building drop animation**: When placed, buildings fall from above with an exponential ease-out curve (`_compute_drop_offset`). A two-tone flickering thrust flame is drawn beneath the falling building (`_draw_thrust_flame`).
- **Drop particles**: Small white particles emitted upward from the landing position as the building settles.
- **Demolish explosion**: When a building is destroyed, coloured particles burst outward in random directions (`_emit_demolish_explosion`).
- **Screen shake**: `ScreenShake` utility applies a random offset to the render position, decaying over time. Used in minigame hit events (e.g., asteroid collision).
- **Cat debug overlay**: When `debug_cat_state` is enabled, a bounding box is drawn around the cat (green when grounded, red when airborne) plus a behaviour label.
- **Building placement preview**: Green highlight for valid placement, red for invalid. In demolish mode, buildings highlight in semi-transparent red on hover.
- **HUD buttons**: Mode toggle (Construct/Demolish), Mine Asteroids, and Alien Evasion buttons with hover highlighting and text labels.

### 4.2 Audio Effects

Audio is managed by the `AudioManager` class in `src/audio.py`. The system supports background music (BGM) playback via `pygame.mixer.music` with volume control. Two music tracks are configured in `config.py`:

- `LIGHT_MUSIC` — played during the light-side base building level.
- `DARK_MUSIC` — played during the dark-side minigames.

Music transitions automatically when entering/exiting minigames. The `play_music_file()` function loads and plays a given path, while `stop_music()` fades out. Volume is controlled via config constants (`DEFAULT_MUSIC_VOLUME`, `DEFAULT_SFX_VOLUME`) and can be adjusted at runtime. Sound effect (SFX) loading and playback functions exist as stubs (`load_sfx`, `play_sfx`) for future implementation.

## 5. Conclusion

### 5.1 Strengths

- **Modular architecture**: The game is cleanly separated into levels, widgets, animations, audio, and UI modules. Each component has a single responsibility.
- **State management**: The App class manages clear game states (MENU, TRANSITION, PLAYING, PAUSED) with smooth transitions.
- **Cat AI**: The autonomous cat with wall-aware jumping, multiple animations, and idle behaviour adds personality to the game.
- **Minigame variety**: Two distinct minigames (asteroid mining + alien evasion) break up the base-building loop.
- **Visual polish**: Particles, drop animations, screen shake, parallax stars, and snow create a polished feel.
- **Debug system**: The `DebugManager` and verbose config flags make development and testing efficient.
- **Save/load**: JSON-based persistence allows the player to resume their colony.

### 5.2 Weaknesses

- **Sound effects**: SFX functions exist but are not yet wired into gameplay events (building placement, demolition, collisions, UI clicks).
- **Cat interaction**: The cat is purely cosmetic — the player cannot feed, pet, or influence it directly.
- **Limited building depth**: Buildings are visual placeholders with no production/efficiency mechanics (e.g., a Workshop doesn't actually produce resources over time).
- **No tutorial**: New players are dropped into the grid without guidance on controls or mechanics.
- **Minigame repetition**: Both minigames lack variety in enemy types, level layouts, or progression mechanics.

### 5.3 Future Enhancements

- **Building functionality**: Each building type could provide passive bonuses (Workshop increases mining yield, Tower reveals map, Observatory detects aliens earlier).
- **Cat care system**: Add feeding, petting, and happiness mechanics that affect cat behaviour.
- **Procedural terrain**: Replace the flat 3-layer ground with Perlin noise-based terrain generation for varied landscapes.
- **Day/night cycle**: Visual cycle with solar-powered building mechanics.
- **Sound effects**: Implement SFX for building placement, demolition, UI hover/click, minigame collisions, and cat meows.
- **Expanded minigames**: More enemy types, power-ups, boss waves, and progressive difficulty curves.
- **Multiplayer**: Cooperative building or competitive resource-gathering.

## 6. Workload Matrix

| Team Member | Contributions |
|-------------|---------------|
|  Kuishbaev Artur | Light level implementation: game logic, UI, save/load system, cat integration, building mechanics, grid system. All code except building assets spritesheet and the sprite-to-building mapping logic. |
|  Htet Wai Aung | Light level building assets: sourced the Buildings.png spritesheet, implemented the cropping logic that maps spritesheet regions to building types in `building_sprites.py`. |
| Shou Heng | Dark Side 1 (LevelDark): Asteroid mining minigame — player ship control, asteroid physics, collision detection, scoring, countdown timer, mining earnings integration. |
| Zhao Yan | Dark Side 2 (LevelDark2): Alien evasion minigame — player movement, enemy AI with 5 move types (dash, shoot, explode, attract, chase), lives system, procedural enemy spawning, difficulty scaling. |

## 7. References

- Pygame Documentation. https://www.pygame.org/docs/
- Python 3 Documentation. https://docs.python.org/3/
- Moon Race source code repository. (local)
- Tutorial exercises.
