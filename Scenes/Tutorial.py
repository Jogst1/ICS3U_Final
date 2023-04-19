#import various classes needed in the main class
import pygame
from Classes.ImageButton import ImageButton
from Classes.TextRenderer import TextRenderer
from Classes.ImageHelper import ImageHelper
from puzzles import puzzle1

#set up some constants
DONE_BUTTON_POSITION = (785, 865)
BACK_BUTTON_POSITION = (410, 865)
NEXT_BUTTON_POSITION = (1150, 865)

FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 36)

class Tutorial():
    """
    The tutorial scene
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

        #import the game scene to switch to when the user is finished the tutorial.
        from Scenes.Game import Game

        #set up some attributes for general class use
        self.screen = screen
        self.images = ImageHelper(screen)
        with open("Assets/Tutorial/tutorial.txt", "r") as data:
            self.pages = data.read().split("<NEWPAGE>\n")
        self.page_index = 0 #keeps track of the current page the user is on
        self.sprite_group = pygame.sprite.Group()

        #set up some buttons and the TextRenderer for displaying the tutorial text, and add them to the spritegroup
        #don't add the back and forward buttons, since they will be rendered individually (and conditionally)
        main_text = TextRenderer(
            self.pages[self.page_index],
            (0, 0, 0),
            FONT,
            pygame.Rect((518, 278), (884, 525))
        )
        def onclick_back_button():
            self.page_index -= 1
            main_text.set_text(self.pages[self.page_index])
        self.back_button = ImageButton(
            self.images.back_button,
            BACK_BUTTON_POSITION,
            onclick_back_button,
            1.05
        )
        def onclick_next_button():
            self.page_index += 1
            main_text.set_text(self.pages[self.page_index])
        self.next_button = ImageButton(
            self.images.next_button,
            NEXT_BUTTON_POSITION,
            onclick_next_button,
            1.05
        )
        done_button = ImageButton(
            self.images.done_button,
            DONE_BUTTON_POSITION,
            lambda: change_fn(Game(screen, puzzle1, change_fn)),
            1.05
        )
        self.sprite_group.add(done_button, main_text)
        
    def update(self):
        """
        Updates the scene.
        """
        pygame.event.get() #keep game running
        #only update the backbutton if it should be visible (i.e. user isn't on first page)
        if self.page_index != 0:
            self.back_button.update()
        #only update the next button if it should be visible (i.e. user isn't on last page)
        if self.page_index != len(self.pages)-1:
            self.next_button.update()
        #update the rest of the spritegroup
        self.sprite_group.update()

    def render(self):
        """
        Renders the scene to the screen
        """
        #blit the background
        self.screen.blit(self.images.background, (0, 0))

        #conditionally blit the back and next buttons, see `self.update` for more details
        if self.page_index != 0:
            self.screen.blit(self.back_button.surf, self.back_button.rect)
        if self.page_index != len(self.pages)-1:
            self.screen.blit(self.next_button.surf, self.next_button.rect)
        
        #blit the rest of the sprite group
        for sprite in self.sprite_group: self.screen.blit(sprite.surf, sprite.rect)
        