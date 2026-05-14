import pygame
from src.menu import create_menus, update_menus, draw_menus, get_main_menu
from src import config
from src.sprites import AnimatedSprite


def main():
    pygame.init()
    
    surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.SCREEN_TITLE)
    
    create_menus()
    main_menu = get_main_menu()
    main_menu.enable()
    
    moon_sprite = AnimatedSprite()
    sprite_group = pygame.sprite.Group(moon_sprite)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        update_menus(events)
        
        surface.fill(config.COLOR_BACKGROUND)
        sprite_group.draw(surface)
        draw_menus(surface)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()