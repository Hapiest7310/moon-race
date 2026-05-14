# Moon Race — Game Plan & Requirements

## Overview

**Course:** CT029-3-2 Imaging and Special Effects  
**Assignment:** Interactive Game Artifact with Special Effects  
**Theme:** Moon  
**Engine:** Pygame (2D)  
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

### Done
- Pygame window (800×600, 60 FPS) > should be full screen. 
- Main menu with animated moon (32-frame spritesheet)
- Level select menu (2 stub entries)
- Options menu (non-functional toggles)
- `AnimatedSprite` class for spritesheet animation
- Moon spritesheet (`MOON.png`)
- Droid Zapper enemy sprites (attack, run, wake, death)
- Pixel planet generator tool
- Virtual environment with pygame, pygame_menu, pygame-ce

### Missing (needs implementation)
- Game loop (playing state separate from menu)
- Player character (movement, abilities, health)
- Two full game levels
- Enemies / obstacles / AI
- Collision detection
- Particle effects (spore burst, healing aura, glowing cap)
- Audio (BGM, SFX)
- Fonts
- Score / progression / win-lose conditions
- Level transition logic
- Fix: moon animation update is never called in main loop
> how about the light side of the moon level will be about builing a city and dark side of the moon will be for collecting resourses by mining asteroids. so the dark level will be a asteroids style minigame and the light level will be something like https://flori9.itch.io/the-final-earth-2. light level should be 2d, pixel stile 
---

## Deliverables

| # | Item | Owner | Due |
|---|------|-------|-----|
| 1 | Narrative storyboard (written) | | |
| 2 | Game levels (code + logic) | | |
| 3 | Visual assets (all sprites, backgrounds, particles) | | |
| 4 | Audio assets (BGM + SFX) | | |
| 5 | Special effects integration | | |
| 6 | Working game executable | | |
| 7 | PDF report | | |
| 8 | Video demo (5–7 min) | | |

---

## Architecture

```
main.py                     ← entry point, orchestrates menus → game
src/
├── __init__.py
├── config.py               ← constants, paths, colors
├── menu.py                 ← main / options / level select menus
├── sprites.py              ← AnimatedSprite class
├── player.py               ← Player character (movement, abilities, health)
├── enemy.py                ← Enemy base class + droid variant
├── particles.py            ← Particle system (burst, aura, glow)
├── camera.py               ← Screen shake, parallax scrolling
├── game.py                 ← Game loop, state machine, collision
├── levels/
│   ├── __init__.py
│   ├── level_base.py       ← Base level class
│   ├── level_1.py          ← Dark Side of the Moon
│   └── level_2.py          ← Light Side of the Moon
assets/
├── images/
│   ├── MOON.png            ← main menu moon spritesheet
│   ├── player/             ← player sprites
│   ├── backgrounds/        ← level backgrounds
│   ├── enemies/            ← enemy sprites (droid zapper, etc.)
│   ├── particles/          ← particle textures
│   └── tiles/              ← terrain / obstacle tiles
├── sounds/
│   ├── bgm/                ← background music
│   └── sfx/                ← sound effects
└── fonts/                  ← custom fonts
levels/                     ← (move to src/levels/ or keep as symlink)
```

---

## Narrative Storyboard

> To be written by the team. Suggested outline:

### Characters
- **Main character:** Astronaut / Moon Rover (player-controlled)  
  Abilities: jump, dash, shoot moon crystals, heal
- **Enemies:** Droid Zappers, Comet Spores, Shadow Moons
- **Boss:** ???

### Abilities
- Movement: left/right, jump, double-jump
- Attack: crystal projectile (with particle burst on impact)
- Special: healing aura (restores health over time)
- Environmental interaction: glowing platforms, gravity zones

### Environment
- **Level 1 — Dark Side of the Moon**  
  Dark, crater-filled terrain. Low gravity. Comet obstacles. Glowing crystal platforms.
- **Level 2 — Light Side of the Moon**  
  Bright lunar surface. Solar flares. Reflective surfaces. Boss arena.

### Plot
> A rogue comet has shattered the Moon Crystal, scattering its fragments across the lunar surface. The player must race through the Dark Side and Light Side to recover the fragments before the comet returns.

### Mechanics
- Comet collision → floor fracture (environmental hazard)
- Spore burst enemies → release poison clouds
- Healing aura → restore health in safe zones
- Glowing cap → temporary invincibility / damage boost

---

## Level Design

### Level 1: Dark Side of the Moon
- **Environment:** Dark, starry background, craters, dim glowing crystals
- **Obstacles:** Craters (pits), falling comets, spore enemies
- **Goal:** Collect 5 moon crystal fragments, reach the portal
- **Special effects:** Comet particle trail, spore burst on enemy death, glowing crystal platforms
- **Length:** ~2–3 min gameplay

### Level 2: Light Side of the Moon
- **Environment:** Bright surface, solar corona in background, reflective metal platforms
- **Obstacles:** Solar flares (timed hazards), laser turrets, boss enemy
- **Goal:** Defeat the boss, collect final crystal fragment
- **Special effects:** Solar flare glow + screen flash, boss attack particles, healing aura zones
- **Length:** ~3–5 min gameplay

---

## Special Effects (required by brief)

| Effect | Where | Technique |
|--------|-------|-----------|
| Spore burst | Enemy death in L1 | Particle system: expanding circle of green particles with fade |
| Healing aura | Safe zones / pickup in L2 | Semi-transparent pulsing circle, lerped color shift (green glow) |
| Glowing cap | Power-up item | Blitting additive-blended glow sprite below item, scale-pulse animation |
| Comet trail | Falling comets in L1 | Particle trail behind moving comet, orange/yellow gradient |
| Solar flare | L2 timed hazard | Full-screen overlay with radial gradient, flashing opacity |
| Screen shake | Collisions / explosions | Offset camera randomly for ~200ms on impact |
| Parallax scrolling | Both levels | Multiple background layers at different scroll speeds |
| Moon rotation | Main menu (already have spritesheet) | Fix update call so animation actually plays |

---

## Audio Plan

### Background Music
- Main menu: ambient space drone
- Level 1: dark, tense lunar theme
- Level 2: bright, energetic theme
- Boss: intense combat track

### Sound Effects
- Player jump, dash, shoot
- Enemy hit, death (spore burst)
- Crystal collect
- Comet impact
- Healing aura activation
- UI button click
- Win / lose jingles

---

## Workload Breakdown (4 students)

| Student | Primary Responsibilities |
|---------|------------------------|
| **A** | Player controller, game loop, collision, physics |
| **B** | Level 1 design, spore burst + comet effects, enemies AI |
| **C** | Level 2 design, solar flare + healing aura effects, boss AI |
| **D** | Audio (BGM + SFX), particle system framework, fonts, UI polish, video demo |

---

## Milestones

### Sprint 1 — Foundation
- [ ] Fix moon animation bug (call `update(dt)` in main loop)
- [ ] Create player class with movement & basic collision
- [ ] Create `game.py` state machine (MENU → PLAYING → PAUSED → GAMEOVER)
- [ ] Particle system base
- [ ] Audio manager base

### Sprint 2 — Level 1
- [ ] Level 1 environment (background, terrain, platforms)
- [ ] Droid Zapper enemy AI
- [ ] Comet obstacle + particle trail
- [ ] Spore burst effect
- [ ] Crystal fragment collectibles
- [ ] Level 1 complete → Level 2 transition

### Sprint 3 — Level 2
- [ ] Level 2 environment (background, platforms, hazards)
- [ ] Solar flare timed hazard + glow effect
- [ ] Healing aura zones
- [ ] Glowing cap power-up
- [ ] Boss enemy + attack patterns

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

- **Pygame CE** (`pygame-ce`) is installed alongside regular `pygame` — prefer `pygame-ce` features (blend modes, improved blitting, built-in shapes)
- `pygame_menu` handles UI; can be extended with custom widgets
- Spritesheet slicing already implemented in `AnimatedSprite` — reuse for player, enemies, effects
- No requirements.txt exists yet — create one from current venv before submission
- Commit frequently, one feature per commit
