import pygame
import typing

from Classes.Instance import Instance, instanceCache, MouseState
from Classes.VolumeSlider import VolumeSlider
from Classes.ImageButton import ImageButton
from Classes.Scenes.MainMenu import MainMenu
from Util.Assets import Assets

class Root(Instance):
    """
    The root instance of the game. Handles blitting to the screen and update calls.
    """
    def __init__(self, parent, screen):
        super().__init__(parent)

        #set up screen to display game and clock to set framerate
        self.clock = pygame.time.Clock()
        self.screen = screen

        #keep track of if game is still running
        self.game_running = True

        #add volume slider and quit button (universal across all screens, so adding them both here)
        self.add_child("volume_slider", VolumeSlider(self))

        pygame.mixer_music.set_volume(0.5)

        def quit(): self.game_running = False
        self.add_child("quit_button", ImageButton(
            self, 
            Assets.quit_button.png,
            quit,
            (1554, 953),
            1.05
        ))

        #add initial scene
        self.add_child("main_menu_scene", MainMenu(self))

    
        while self.game_running:
            deltaTime = self.clock.tick(60) / 1000
            events = pygame.event.get()
            pressed = pygame.mouse.get_pressed()
            mouseState = MouseState(
                pygame.mouse.get_pos(),
                (pressed[0], pressed[2])
            )

            self.screen.fill((255, 255, 255))


            allRenderables = []
            for instance in instanceCache.copy():
                instance.update(events, mouseState, deltaTime)
                allRenderables.extend(instance.renderables.values())

            allRenderables.sort(key=lambda r: r[1], reverse=True)

            for renderable in allRenderables:
                if isinstance(renderable[0], tuple):
                    self.screen.blit(renderable[0][0], renderable[0][1])
                elif isinstance(renderable[0], pygame.Surface):
                    self.screen.blit(renderable[0], renderable[0].get_rect())
                elif isinstance(renderable[0], typing.Callable):
                    renderable[0](self.screen)
            pygame.display.flip()
