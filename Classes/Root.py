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

        #set the initial volume levels
        pygame.mixer_music.set_volume(0)

        #add volume slider and quit button (universal across all screens, so adding them both here)
        self.add_child("volume_slider", VolumeSlider(self))
        def end(): self.game_running = False
        self.add_child("quit_button", ImageButton(
            self, 
            Assets.quit_button.png,
            end,
            (1554, 953),
            1.05
        ))

        #add initial scene
        self.add_child("main_menu_scene", MainMenu(self))
    

        #the main game loop. loops while game_running is true.
        while self.game_running:
            #get the deltaTime, which is the time elapsed since the last frame, in seconds.
            #i used this unity docs page to better understand deltatime: https://docs.unity3d.com/ScriptReference/Time-deltaTime.html 
            #i also used this stackoverflow question to originally find out how to get the deltatime: 
            # https://stackoverflow.com/questions/24039804/pygame-current-time-millis-and-delta-time
            deltaTime = self.clock.tick(60) / 1000
            #get a list of events for this frame
            events = pygame.event.get()
            #construct a mouseState object with info about the position of the mouse, and the state of the rmb and lmb buttons
            pressed = pygame.mouse.get_pressed()
            mouseState = MouseState(
                pygame.mouse.get_pos(),
                (pressed[0], pressed[2])
            )

            #set up a list of all the renderables
            allRenderables = []
            #loop through all instances in the cache. copy here because some may be removed during the updates, which throws an error
            for instance in instanceCache.copy():
                #update the instance, passing in the events, deltatime, and mouse state
                instance.update(events, mouseState, deltaTime)
                #add the instance's renderables to the list of all renderables
                allRenderables.extend(instance.renderables.values())

            #sort all renderables by their Z Index, so they render in the correct order
            allRenderables.sort(key=lambda r: r[1], reverse=True)

            #loop through all of the renderables
            for renderable in allRenderables:
                #if renderable is in the form ((surf, rect), zIndex)
                if isinstance(renderable[0], tuple):
                    #blit it to the screen
                    self.screen.blit(renderable[0][0], renderable[0][1])
                #if renderable is in the form (surf, zIndex)
                elif isinstance(renderable[0], pygame.Surface):
                    #blit it to the screen, getting its rect with the get_rect fn
                    self.screen.blit(renderable[0], renderable[0].get_rect())
                #if renderable is in the form (function, zIndex)
                elif isinstance(renderable[0], typing.Callable):
                    #call the function, passing in the screen
                    #the function will handle any blitting (or actually drawing is what the function form tends to be used for)
                    renderable[0](self.screen)

            #update the actual screen
            pygame.display.flip()
