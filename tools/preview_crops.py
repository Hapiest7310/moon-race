# tools/preview_crops.py  — run standalone to check your sprite_rect values
import pygame, sys
from src import config

pygame.init()
screen = pygame.display.set_mode((800, 600))
sheet = pygame.image.load("assets/images/Buildings.png").convert_alpha()

for bt in config.BUILDING_TYPES:
    r = bt.get("sprite_rect")
    if not r: continue
    x1, y1, x2, y2 = r
    cropped = sheet.subsurface(pygame.Rect(x1, y1, x2-x1, y2-y1))
    scaled = pygame.transform.smoothscale(cropped, (200, 200))
    screen.fill((30, 30, 30))
    screen.blit(scaled, (300, 200))
    font = pygame.font.SysFont(None, 36)
    screen.blit(font.render(bt["name"], True, (255,255,255)), (10, 10))
    pygame.display.flip()
    pygame.time.wait(1500)

pygame.quit()