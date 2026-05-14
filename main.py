import pygame
from src.menu import create_menus, get_main_menu
from src import config
from src.app import App


def main():
    pygame.init()

    surface = pygame.display.set_mode(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
        pygame.FULLSCREEN
    )
    pygame.display.set_caption(config.SCREEN_TITLE)

    create_menus()
    main_menu = get_main_menu()
    main_menu.enable()

    app = App(surface)
    app.run()

    pygame.quit()


if __name__ == "__main__":
    main()
