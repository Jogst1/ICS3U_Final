import pygame

MICROCONTROLLER_IMAGE = pygame.image.load("Assets/Game/microcontroller.png").convert_alpha(pygame.display.get_surface())

class Microcontroller(pygame.sprite.Sprite):

    def __init__(self, position: tuple[int]):
        super().__init__()

        self.surf = MICROCONTROLLER_IMAGE
        self.rect = self.surf.get_rect()
        self.rect.topleft = position

class MicroPointer():
    def __init__(self, pointTo, portId):
        self.pointTo = pointTo
        self.portId = portId