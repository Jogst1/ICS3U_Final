import pygame
from Classes.Instance import Instance, MouseState

#rect for checking if mouse is in the adjust area
VOLUME_ADJUST_RECT = pygame.Rect(0, 25, 35, 150)

class VolumeSlider(Instance):
    def __init__(self, parent):
        super().__init__(parent)

        self.open = False
        self.debounce = False

        #set up the volume icon, with zindex 1
        self.renderables["icon"] = (
            pygame.transform.smoothscale(
                pygame.image.load("Assets/volume_icon.png")
                    .convert_alpha(self.parent.screen),
                (25, 25)
            ),
            -1
        )

        def draw_bar(screen: pygame.Surface):
            if self.open:
                pygame.draw.line(screen, (25, 25, 25), (11, 25), (11, 25+100), 10)
        self.renderables["bar"] = (
            draw_bar,
            -1
        )

        def draw_slider(screen: pygame.Surface):
            volume = pygame.mixer_music.get_volume()
            if self.open:
                pygame.draw.line(screen, (100, 149, 237), (3, 125-(100*volume)), (20, 125-(100*volume)), 3)
        self.renderables["slider"] = (
            draw_slider,
            -2
        )
    
    def update(self, _: list[pygame.event.Event], mouseState: MouseState, __: float):
        if mouseState.lmb:
            if (
                self.renderables["icon"][0].get_rect().collidepoint(mouseState.x, mouseState.y)
                and (not self.debounce)
            ):
                self.open = not self.open
            
            if VOLUME_ADJUST_RECT.collidepoint(mouseState.x, mouseState.y) and self.open:
                pygame.mixer_music.set_volume(max(0, (125-mouseState.y)/100))
            self.debounce = True
        else:
            self.debounce = False