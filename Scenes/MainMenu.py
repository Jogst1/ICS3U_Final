#import various classes needed in the main class
import pygame
from Classes.ImageButton import ImageButton
from Classes.ImageHelper import ImageHelper

#set up some constants
START_BUTTON_POSITION = (526, 452)
CREDITS_BUTTON_POSITION = (489, 676)

class MainMenu:
    """
    The main menu of the game.
    """
    def __init__(self, screen: pygame.Surface, change_fn):
        """
        Parameters
        ----------
        screen:
            The Surface to blit to.
        change_fn:
            A function that changes the scene when provided with a new one.
        """

        #import potential next scenes
        #i am importing these in the __init__ method since if I import them at the top of the file, it would cause a circular import which is an error
        from Scenes.Credits import Credits
        from Scenes.Tutorial import Tutorial

        #set up some attributes for general class use
        self.screen = screen
        self.images = ImageHelper(screen)
        self.sprite_group = pygame.sprite.Group()
        
        #set up some buttons using the ImageButton class, and add them to the spritegroup
        start_button = ImageButton(self.images.start_button, 
                                    START_BUTTON_POSITION, 
                                    lambda: change_fn(Tutorial(screen, change_fn)),
                                    1.05
                                  )
        credits_button = ImageButton(self.images.credits_button,
                                     CREDITS_BUTTON_POSITION,
                                     lambda: change_fn(Credits(screen, change_fn)),
                                     1.05
                                    )
        self.sprite_group.add(start_button, credits_button)

    def update(self):
        """
        Updates the scene, in this case updating the buttons.
        """
        self.sprite_group.update()
        pygame.event.get() #keep game running
    
    def render(self):
        """
        Renders the scene to the screen
        """
        self.screen.blit(self.images.background, (0, 0))
        for sprite in self.sprite_group: self.screen.blit(sprite.surf, sprite.rect)