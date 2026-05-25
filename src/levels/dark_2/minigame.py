import pygame
import random
import time
import math
import os


def load_sound_safe(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        # audio not available, continue without sound
        pass

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("sample effect")
    clock = pygame.time.Clock()

    # Try to load background music and collision sound if present in ./asset
    asset_dir = os.path.join(os.path.dirname(__file__), "lab", "asset")
    bg_music_path = os.path.join(asset_dir, "backgroundMusic.mp3")
    punch_path = os.path.join(asset_dir, "punch.mp3")

    if os.path.exists(bg_music_path):
        try:
            pygame.mixer.music.load(bg_music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    collisionSound = None
    if os.path.exists(punch_path):
        try:
            collisionSound = pygame.mixer.Sound(punch_path)
            collisionSound.set_volume(0.5)
        except Exception:
            collisionSound = None

    # Font availability: some systems ship pygame without font module support.
    # Try to initialize font; if unavailable we'll draw a simple block-letter
    # fallback for the victory text.
    font = None
    font_available = False
    try:
        pygame.font.init()
        font = pygame.font.SysFont(None, 72)
        font_available = True
    except Exception:
        font = None
        font_available = False

    # Character: use a simple circle surface instead of external SVG so the game
    # runs out of the box. If an image file exists, try to use it.
    char_surf = None
    char_img_path = os.path.join(asset_dir, "characters.png")
    if os.path.exists(char_img_path):
        try:
            img = pygame.image.load(char_img_path).convert_alpha()
            char_surf = pygame.transform.smoothscale(img, (64, 64))
        except Exception:
            char_surf = None

    if char_surf is None:
        char_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(char_surf, (30, 144, 255), (24, 24), 22)
        pygame.draw.circle(char_surf, (255, 255, 255), (18, 18), 6)

    updatedCharacter = char_surf
    charRectBlock = updatedCharacter.get_rect(center=(400, 500))

    velocityX, velocityY = 0.0, 0.0
    acceleration, maxSpeed, friction = 0.5, 5, 0.1
    movementCounts = {"left": 1, "right": 1, "up": 1, "down": 1}

    blinkDuration, blinkCounter = 30, 0
    isBlinking = False

    enemyList = [{
        "pos": [random.randint(0, 800), random.randint(0, 600)],
        "radius": 10,
        "color": (255, 0, 0),
    }]

    enemySpeed = 2
    lastCollisionTime = time.time()
    lastBallAddTime = time.time()
    shattered = False
    fragments = []
    showVictory = False
    victoryDelayStart = None

    running = True
    while running:
        screen.fill((255, 255, 255))

        currentTime = time.time()
        timeSinceLastCollision = currentTime - lastCollisionTime

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if showVictory and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            velocityX -= acceleration
            movementCounts["left"] += 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            velocityX += acceleration
            movementCounts["right"] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            velocityY -= acceleration
            movementCounts["up"] += 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            velocityY += acceleration
            movementCounts["down"] += 1

        # Apply friction
        velocityX = max(-maxSpeed, min(maxSpeed, velocityX - friction * (1 if velocityX > 0 else -1)))
        velocityY = max(-maxSpeed, min(maxSpeed, velocityY - friction * (1 if velocityY > 0 else -1)))

        # Move character and clamp to screen
        charRectBlock.x += int(velocityX)
        charRectBlock.y += int(velocityY)
        charRectBlock.clamp_ip(screen.get_rect())

        # scale enemy balls size
        if timeSinceLastCollision > 10:
            for enemy in enemyList:
                enemy["radius"] = min(enemy["radius"] * 1.1, 20)

        # Add new enemy ball (random color and position)
        if currentTime - lastBallAddTime > 5 and not shattered:
            newColor = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            enemyList.append({
                "pos": [random.randint(0, 800), random.randint(0, 600)],
                "radius": 10,
                "color": newColor,
            })
            lastBallAddTime = currentTime

        # Predict movement
        totalMoves = sum(movementCounts.values())
        moveProb = {k: movementCounts[k] / totalMoves for k in movementCounts}
        predictedX = 5 * (moveProb["right"] - moveProb["left"])
        predictedY = 5 * (moveProb["down"] - moveProb["up"])
        predictedPos = [charRectBlock.centerx + predictedX, charRectBlock.centery + predictedY]

        # Enemy chasing - update positions
        for i, enemy in enumerate(enemyList):
            chaseX = predictedPos[0] - enemy["pos"][0]
            chaseY = predictedPos[1] - enemy["pos"][1]
            dist = max(1, math.hypot(chaseX, chaseY))

            # Avoid overlapping with other enemies
            for j, other in enumerate(enemyList):
                if i != j:
                    dx = enemy["pos"][0] - other["pos"][0]
                    dy = enemy["pos"][1] - other["pos"][1]
                    d = math.hypot(dx, dy)
                    if d < enemy["radius"] + other["radius"] and d != 0:
                        enemy["pos"][0] += dx / d
                        enemy["pos"][1] += dy / d
                    elif d == 0:
                        enemy["pos"][0] += 1

            # Move enemy toward the character position
            enemy["pos"][0] += enemySpeed * chaseX / dist
            enemy["pos"][1] += enemySpeed * chaseY / dist

            # Check collision - if yes update the variable value
            enemyRect = pygame.Rect(enemy["pos"][0] - enemy["radius"], enemy["pos"][1] - enemy["radius"],
                                     enemy["radius"] * 2, enemy["radius"] * 2)
            if charRectBlock.colliderect(enemyRect) and not shattered:
                if collisionSound:
                    try:
                        collisionSound.play()
                    except Exception:
                        pass
                lastCollisionTime = currentTime
                lastBallAddTime = currentTime
                shattered = False
                fragments.clear()
                isBlinking = True
                blinkCounter = blinkDuration
                # Reset to original ball only keep first
                if len(enemyList) > 0:
                    enemyList = [enemyList[0]]

        # trigger the Blinking effect
        if isBlinking:
            blinkCounter -= 1
            if blinkCounter <= 0:
                isBlinking = False
            elif blinkCounter % 10 < 5:
                screen.blit(updatedCharacter, charRectBlock)
        else:
            screen.blit(updatedCharacter, charRectBlock)

        # game over effect Shatter the ball
        if timeSinceLastCollision > 15 and not shattered and len(enemyList) >= 1:
            shattered = True
            for enemy in enemyList:
                for k in range(10):
                    angle = k * (360 / 10)
                    radians = math.radians(angle)
                    fragments.append({
                        "x": enemy["pos"][0],
                        "y": enemy["pos"][1],
                        "vx": math.cos(radians) * 1.2,
                        "vy": math.sin(radians) * 1.2,
                        "radius": 5,
                        "color": enemy["color"],
                    })
            showVictory = True
            victoryDelayStart = currentTime

        # render the ball(s)
        if not shattered:
            for enemy in enemyList:
                pygame.draw.circle(screen, enemy["color"], (int(enemy["pos"][0]), int(enemy["pos"][1])),
                                   int(enemy["radius"]))

        # Draw shattered fragments
        if shattered:
            for frag in fragments:
                frag["x"] += frag["vx"]
                frag["y"] += frag["vy"]
                pygame.draw.circle(screen, frag["color"], (int(frag["x"]), int(frag["y"])), frag["radius"])

        # ending - Show victory text
        if showVictory:
            if victoryDelayStart is not None and currentTime - victoryDelayStart >= 2:
                if font_available and font is not None:
                    victoryText = font.render("Victory!", True, (255, 255, 0))
                    screen.blit(victoryText, (300, 250))
                    # instruct how to quit
                    try:
                        small = pygame.font.SysFont(None, 24)
                        hint = small.render("Press ESC to exit", True, (0, 0, 0))
                        screen.blit(hint, (320, 330))
                    except Exception:
                        # ignore if small font unavailable
                        pass
                else:
                    # Fallback: draw block letters for "Victory!" if font module
                    # is not available. This is a minimal renderer using 5x5
                    # pixel blocks for the letters used.
                    def draw_block_text(surf, text, topleft, block_size=8, spacing=2, color=(255, 255, 0)):
                        # patterns for the letters V I C T O R Y ! (5x5 grids)
                        patterns = {
                            "V": [
                                "10001",
                                "10001",
                                "10001",
                                "01010",
                                "00100",
                            ],
                            "I": [
                                "11111",
                                "00100",
                                "00100",
                                "00100",
                                "11111",
                            ],
                            "C": [
                                "01110",
                                "10001",
                                "10000",
                                "10001",
                                "01110",
                            ],
                            "T": [
                                "11111",
                                "00100",
                                "00100",
                                "00100",
                                "00100",
                            ],
                            "O": [
                                "01110",
                                "10001",
                                "10001",
                                "10001",
                                "01110",
                            ],
                            "R": [
                                "11110",
                                "10001",
                                "11110",
                                "10100",
                                "10010",
                            ],
                            "Y": [
                                "10001",
                                "01010",
                                "00100",
                                "00100",
                                "00100",
                            ],
                            "!": [
                                "00100",
                                "00100",
                                "00100",
                                "00000",
                                "00100",
                            ],
                        }

                        x, y = topleft
                        for ch in text:
                            pat = patterns.get(ch.upper())
                            if pat is None:
                                # skip unknown characters with spacing
                                x += (5 * block_size) + spacing
                                continue
                            for row_i, row in enumerate(pat):
                                for col_i, c in enumerate(row):
                                    if c == "1":
                                        rect = pygame.Rect(
                                            x + col_i * block_size,
                                            y + row_i * block_size,
                                            block_size,
                                            block_size,
                                        )
                                        pygame.draw.rect(surf, color, rect)
                            x += (5 * block_size) + spacing

                    draw_block_text(screen, "VICTORY!", (280, 240), block_size=10, spacing=6, color=(255, 215, 0))
                    # simple hint rectangle for quit
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(320, 330, 160, 28), 0)
                    # tiny dot pattern for the hint ("Press ESC to exit")
                    # draw three small rectangles representing the hint
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(328, 336, 8, 8))
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(346, 336, 8, 8))
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(364, 336, 8, 8))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
