# Moon Race — Game Plan & Requirements

## Overview

**Course:** CT029-3-2 Imaging and Special Effects  
**Assignment:** Interactive Game Artifact with Special Effects  
**Theme:** Moon  
**Engine:** Pygame CE 2.5.7 (2D)  
**Team Size:** 4 students  
**Weight:** 60% of module  

---

## Requirements Checklist (from assignment brief)
> no need to include things that are not coding related 
- [ ] Moon-themed interactive game
- [ ] At least **2 levels** with unique challenges & environments
- [ ] Narrative storyboard (characters, abilities, environment, plot, mechanics)
- [ ] Visual assets: backgrounds, sprites, textures, animations, particle effects
- [ ] Audio assets: background music + sound effects (noise, voice, clips)
- [ ] Special effects on attacks / major events (spore burst, healing aura, glowing cap, etc.)
- [x] Event-driven gameplay
- [ ] Report (PDF): intro, narrative, screenshots, effect explanations, conclusion, workload matrix, references
- [ ] 5–7 minute video demo
- [ ] Submit complete game files (code, assets, audio) in zip

---

## Current Project State

### Done (code infrastructure)
- [x] Fullscreen 1920×1080 window at 60 FPS
- [x] State machine: `MENU → TRANSITION → PLAYING → (ESC) → PAUSED → (Continue/Quit)`
- [x] Menu system with 7 submenus (Main, Start, New/Load, Options → Keybindings/Sound, Pause, Sound from Pause)
- [x] Loading spinner (spinning moon, event-driven `start/stop` API)
- [x] `AnimatedSprite` class for spritesheet animation
- [x] `pygame_menu`-based overlay HUD with multi-line debug output
- [x] **Light Side level** (`level_light.py`):
  - Grid system (bottom-left origin, 32px cells, 60×33 grid)
  - Color picker widget (8 colors, local coordinates) — legacy
  - Building placement with support checks, overlap detection, cost validation
  - Building drop animation (exponential ease-out, thrust flame, particles)
  - Building Menu widget (type selector with size/cost display)
  - Save/load to JSON files in `saves/`
  - "Mine Asteroids" button to enter dark side minigame
- [x] **Dark Side level** (`level_dark.py`): Full Asteroids clone
  - Ship (triangle), asteroids (irregular polygons), bullets (circles)
  - Particles (explosion debris, thrust exhaust)
  - Screen shake on collisions
  - Wave progression (`min(3+wave, 18)` asteroids per wave)
  - Countdown before gameplay (`DARK_COUNTDOWN_SECONDS`)
  - Game-over restart → return to light level with coins
  - `ShaderSurface` class for blend-mode compositing (BLEND_ADD glow layers)
- [x] Widget system (`src/widget/`: base class + ColorPicker + BuildingMenu)
- [x] Comprehensive debug system (master toggle + 10 sub-flags)
- [x] Virtual environment with `pygame-ce`, `pygame_menu`
- [x] Moon spritesheet (`MOON.png`) and Droid Zapper enemy sprites
- [x] Moon animation fix (update call in main loop)
- [x] Pixel planet generator tool
- [x] Audio system (BGM + SFX, volume sliders, graceful degradation)
- [x] Minigame switching (light→dark→light with coin transfer)
- [x] Save/load system (JSON, per-save-file, auto-save on build)
- [x] Pause system (ESC → dim overlay → pause menu)

### Needs implementation
- Dark Side: Droid Zapper enemy AI, obstacles/craters, spore burst effect, collectible crystals
- Dark Side: Parallax scrolling, comet obstacle with particle trail
- Light Side: Solar flare hazard, healing aura zones, glowing cap power-up
- Light Side: NPCs / population system
- Full: Win/lose conditions, score display (beyond mining coins)
- Dark Side: Comets, Droid Zappers, crystal fragments, spore burst
- Full: Audio SFX for dark side events (shoot, explosion, pickup)

---

## Architecture (current)

```
main.py                     ← entry point (init, fullscreen, launch App)
music/
└── 11.mp3                  ← Background music track
src/
├── __init__.py
├── audio.py                ← Audio manager (BGM + SFX)
├── config.py               ← constants, debug flags, building types, save name
├── app.py                  ← state machine (MENU → TRANSITION → PLAYING / PAUSED)
├── menu.py                 ← 7 pygame_menu UI menus
├── sprites.py              ← AnimatedSprite class
├── spinner.py              ← module-level loading spinner singleton
├── grid.py                 ← bottom-left origin grid (Light Side)
├── widget/
│   ├── __init__.py         ← Widget base class
│   ├── color_picker.py     ← 8-color palette widget (legacy)
│   └── building_menu.py    ← Building type selector with cost display
└── levels/
    ├── __init__.py
    ├── level_base.py       ← abstract Level interface
    ├── level_light.py      ← Light Side (city-builder, save/load, drop animation)
    └── level_dark.py       ← Dark Side (Asteroids clone, ShaderSurface)
assets/
├── images/
│   ├── MOON.png            ← main menu moon spritesheet
│   ├── player/             ← player sprites (empty)
│   ├── backgrounds/        ← level backgrounds (empty)
│   ├── enemies/            ← Droid Zapper sprite sheets
│   ├── particles/          ← particle textures (empty)
│   └── tiles/              ← terrain / obstacle tiles (empty)
├── sounds/
│   ├── bgm/                ← background music (empty now — music/ is used instead)
│   └── sfx/                ← sound effects (empty)
└── fonts/                  ← custom fonts (empty)
```

---

## Level Design

### Level 1 (Dark Side of the Moon) — Asteroids-mining
- **Environment:** Black starfield with Asteroid belt
- **Obstacles:** Asteroids (3 sizes), split on destruction
- **Goal:** Mine asteroids for score/coins
- **Special effects:** Screen shake, additive glow layers, particle explosions, thrust particles
- **Status:** ✅ Full Asteroids clone with ship/asteroids/bullets/particles/waves

### Level 2 (Light Side of the Moon) — City-builder (inspired by The Final Earth 2)
- **Environment:** Bright surface, 32px grid, star overlay
- **Obstacles:** Resource constraints (money), support requirements
- **Goal:** Build a lunar city, earn coins from mining
- **Current features:** Grid, building placement with drop animation, save/load, building menu, "Mine Asteroids" button → dark side minigame
- **Needs:** Solar flare hazard, NPCs, population system, win/lose conditions

---

## Special Effects (required by brief)

| Effect | Where | Technique | Status |
|--------|-------|-----------|--------|
| Spore burst | Enemy death in L1 | Particle system: expanding circle of green particles with fade | ❌ |
| Healing aura | Safe zones / pickup in L2 | Semi-transparent pulsing circle, lerped color shift (green glow) | ❌ |
| Glowing cap | Power-up item | Blitting additive-blended glow sprite below item, scale-pulse animation | ❌ |
| Comet trail | Falling comets in L1 | Particle trail behind moving comet, orange/yellow gradient | ❌ |
| Solar flare | L2 timed hazard | Full-screen overlay with radial gradient, flashing opacity | ❌ |
| Screen shake | Collisions / explosions | Offset camera randomly for ~200ms on impact | ✅ Dark Side |
| Parallax scrolling | Both levels | Multiple background layers at different scroll speeds | ❌ |
| Additive glow | Ship/bullets in L1 | ShaderSurface with BLEND_ADD compositing | ✅ |
| Thrust particles | Ship thrust / building drop | Damped-velocity circle particles with fade | ✅ |
| Explosion particles | Asteroid destruction | Velocity-damped coloured circle particles | ✅ |
| Building drop | Building placement | Exponential ease-out + thrust flame + particles | ✅ |

---

## Milestones

### Sprint 1 — Foundation (DONE)
- [x] Fix moon animation bug (call `update(dt)` in main loop)
- [x] Create menu system with Start, Options, Quit
- [x] Create App state machine (MENU → TRANSITION → PLAYING)
- [x] Loading spinner API
- [x] Grid system with bottom-left origin
- [x] Widget system with ColorPicker
- [x] Light Side level scaffold (grid + paint + debug)
- [x] Debug system (10 flags + FPS + overlay HUD)

### Sprint 2 — Level 1 (Dark Side)
- [x] **Full Asteroids clone** (ship, asteroids, bullets, particles, waves)
- [x] **ShaderSurface** (additive blend compositing for glow layers)
- [x] **Screen shake** on collision
- [x] **Particle effects** (explosion debris, thrust exhaust)
- [x] **Countdown** before gameplay
- [x] **Minigame integration** (play from Light Side, exit with coins)
- [ ] Droid Zapper enemy AI
- [ ] Comet obstacle + particle trail
- [ ] Spore burst effect
- [ ] Crystal fragment collectibles

### Sprint 3 — Level 2 (Light Side)
- [x] **Building placement** (support, cost, overlap checks)
- [x] **Building drop animation** (exponential ease-out, thrust flame, particles)
- [x] **Building menu** (type selector with cost display)
- [x] **Save/load system** (JSON, per-save-file)
- [x] **Audio system** (BGM + SFX, volume sliders)
- [x] **Pause system** (ESC → dim overlay → pause menu)
- [ ] Solar flare timed hazard + glow effect
- [ ] Healing aura zones
- [ ] Glowing cap power-up
- [ ] NPCs / population system

### Sprint 4 — Polish & Deliverables
- [ ] Audio SFX for dark side (shoot, explosion, pickups)
- [ ] Parallax scrolling
- [ ] Score display, win/lose screens
- [ ] PDF report
- [ ] Video demo recording
- [ ] Final zip submission

---

## Technical Notes

- **Pygame CE** only (`pygame-ce` 2.5.7) — do NOT install `pygame` alongside it (causes SDL blit conflicts)
- `pygame_menu` handles UI menus and the in-game overlay HUD
- Spritesheet slicing via `AnimatedSprite.subsurface()` — reuse for player, enemies, effects
- All widget coordinates are **local** (relative to widget rect) — only convert to absolute at draw time
- Grid uses **bottom-left origin** (gy=0 at screen bottom, y increases upward)
- Debug system: master `debug` flag in `config.py` — set to `False` to disable all debug output
- `requirements.txt` includes: `pygame-ce`, `pygame-menu`, `pyperclip`, `typing-extensions`
- **ShaderSurface** wraps `pygame.Surface(SRCALPHA)` for BLEND_ADD compositing — can be replaced with OpenGL framebuffer for real GLSL shaders
- **Building drop** uses exponential ease-out: `offset = (1 - e^(-4p)) / (1 - e^(-4))` for fast-start / dramatic deceleration
