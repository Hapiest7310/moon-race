import pygame
import pygame_gui
from pygame_gui._constants import UI_BUTTON_PRESSED
from sprites import AnimatedSprite


def main():
    pygame.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Moon Race")
    
    ui_manager = pygame_gui.UIManager((800, 600))
    
    sprite_group = pygame.sprite.Group()
    moon_sprite = AnimatedSprite(400, 150, "assets/images/MOON.png", frame_count=32, animation_speed=80)
    sprite_group.add(moon_sprite)
    
    title_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((200, 80), (400, 60)),
        text="Moon Race",
        manager=ui_manager
    )
    
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((300, 280), (200, 50)),
        text="Start Game",
        manager=ui_manager
    )
    
    options_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((300, 350), (200, 50)),
        text="Options",
        manager=ui_manager
    )
    
    quit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((300, 420), (200, 50)),
        text="Quit",
        manager=ui_manager
    )
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            ui_manager.process_events(event)
            
            if event.type == UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    print("Starting Moon Race...")
                elif event.ui_element == options_button:
                    print("Opening options...")
                elif event.ui_element == quit_button:
                    running = False
        
        sprite_group.update(time_delta * 1000)
        ui_manager.update(time_delta)
        
        screen.fill((20, 20, 40))
        sprite_group.draw(screen)
        ui_manager.draw_ui(screen)
        pygame.display.update()
    
    pygame.quit()


if __name__ == "__main__":
    main()
