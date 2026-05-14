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
- [ ] Event-driven gameplay
- [ ] Report (PDF): intro, narrative, screenshots, effect explanations, conclusion, workload matrix, references
- [ ] 5–7 minute video demo
- [ ] Submit complete game files (code, assets, audio) in zip

---

## Current Project State

### Done (code infrastructure)
- [x] Fullscreen 1920×1080 window at 60 FPS
- [x] State machine: `MENU → TRANSITION → PLAYING → (ESC) → MENU`
- [x] Menu system with 3 submenus (Start → Load/New/Back, Options → Keybindings/Sound/Back, Quit)
- [x] Loading spinner (spinning moon, event-driven `start/stop` API)
- [x] `AnimatedSprite` class for spritesheet animation
- [x] `pygame_menu`-based overlay HUD with multi-line debug output
- [x] **Light Side level** (`level_light.py`):
  - Grid system (bottom-left origin, 32px cells, 60×33 grid)
  - Color picker widget (8 colors, local coordinates)
  - Cell painting (click to paint, hover to highlight)
  - Layer separation (widget layer vs grid layer)
  - Debug overlay (FPS, mouse coords, hover, widget state, cell count, grid info)
- [x] **Dark Side level** stub (`level_dark.py`)
- [x] Widget system (`src/widget/`: base class + ColorPicker)
- [x] Comprehensive debug system (master toggle + 10 sub-flags)
- [x] Virtual environment with `pygame-ce`, `pygame_menu`
- [x] Moon spritesheet (`MOON.png`) and Droid Zapper enemy sprites
- [x] Moon animation fix (update call in main loop)
- [x] Pixel planet generator tool

### Missing (needs implementation)
- Player character (movement, abilities, health)
- Dark Side level gameplay (Asteroids-mining style)
- City-builder mechanics for Light Side level
- Enemies / obstacles / AI
- Collision detection
- Particle effects (spore burst, healing aura, glowing cap, comet trail, solar flare)
- Audio (BGM, SFX)
- Fonts
- Score / progression / win-lose conditions
- Level transition logic
- Screen shake, parallax scrolling, camera effects

---

## Architecture (current)

```
main.py                     ← entry point (init, fullscreen, launch App)
src/
├── __init__.py
├── config.py               ← constants, debug flags, FPS accessor
├── app.py                  ← state machine (MENU → TRANSITION → PLAYING)
├── menu.py                 ← pygame_menu UI (Start, Options, Quit)
├── sprites.py              ← AnimatedSprite class
├── spinner.py              ← module-level loading spinner singleton
├── grid.py                 ← bottom-left origin grid (Light Side)
├── widget/
│   ├── __init__.py         ← Widget base class
│   └── color_picker.py     ← 8-color palette widget
└── levels/
    ├── __init__.py
    ├── level_base.py       ← abstract Level interface
    ├── level_light.py      ← Light Side (city-builder)
    └── level_dark.py       ← Dark Side stub (Asteroids-style)
assets/
├── images/
│   ├── MOON.png            ← main menu moon spritesheet
│   ├── player/             ← player sprites (empty)
│   ├── backgrounds/        ← level backgrounds (empty)
│   ├── enemies/            ← Droid Zapper sprite sheets
│   ├── particles/          ← particle textures (empty)
│   └── tiles/              ← terrain / obstacle tiles (empty)
├── sounds/
│   ├── bgm/                ← background music (empty)
│   └── sfx/                ← sound effects (empty)
└── fonts/                  ← custom fonts (empty)
```

---

## Level Design

### Level 1 (Dark Side of the Moon) — Asteroids-mining
- **Environment:** Dark, starry background, craters, dim glowing crystals
- **Obstacles:** Craters (pits), falling comets, spore enemies
- **Goal:** Collect moon crystal fragments by mining asteroids
- **Special effects:** Comet particle trail, spore burst on enemy death, glowing crystal platforms
- **Status:** Stub — fill `level_dark.py`

### Level 2 (Light Side of the Moon) — City-builder (inspired by The Final Earth 2)
- **Environment:** Bright surface, solar corona in background, 32px grid system
- **Obstacles:** Solar flares (timed hazards), resource constraints
- **Goal:** Build a lunar city, manage resources, survive hazards
- **Current features:** Grid with bottom-left origin, color picker widget, cell painting, debug overlay
- **Needs:** Building placement, resource system, NPCs, win/lose conditions

---

## Special Effects (required by brief — all TODO)

| Effect | Where | Technique |
|--------|-------|-----------|
| Spore burst | Enemy death in L1 | Particle system: expanding circle of green particles with fade |
| Healing aura | Safe zones / pickup in L2 | Semi-transparent pulsing circle, lerped color shift (green glow) |
| Glowing cap | Power-up item | Blitting additive-blended glow sprite below item, scale-pulse animation |
| Comet trail | Falling comets in L1 | Particle trail behind moving comet, orange/yellow gradient |
| Solar flare | L2 timed hazard | Full-screen overlay with radial gradient, flashing opacity |
| Screen shake | Collisions / explosions | Offset camera randomly for ~200ms on impact |
| Parallax scrolling | Both levels | Multiple background layers at different scroll speeds |

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
- [ ] Level 1 environment (background, terrain, platforms)
- [ ] Droid Zapper enemy AI
- [ ] Comet obstacle + particle trail
- [ ] Spore burst effect
- [ ] Crystal fragment collectibles
- [ ] Level 1 complete → Level 2 transition

### Sprint 3 — Level 2 (Light Side)
- [ ] City-builder mechanics (building placement, resources)
- [ ] Solar flare timed hazard + glow effect
- [ ] Healing aura zones
- [ ] Glowing cap power-up
- [ ] NPCs / population system

### Sprint 4 — Polish & Deliverables
- [ ] Audio integration (all BGM + SFX)
- [ ] Screen shake & camera effects
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
