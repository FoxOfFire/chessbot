import pygame


def main() -> None:

    pygame.init()
    window_dimension = (600, 600)
    pygame.display.set_mode(
        size=window_dimension,
        flags=pygame.DOUBLEBUF,
    )
    clock = pygame.time.Clock()

    display = pygame.display.get_surface()

    display.fill((10, 10, 10))
    pygame.display.flip()

    clock.tick(60)
