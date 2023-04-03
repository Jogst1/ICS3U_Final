#import and initialize pygame
import pygame
pygame.init()
#import the main menu as a default scene
from Scenes.MainMenu import MainMenu

# Set up some constants:
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

#main section:
#set up a screen object with a 1920x1080 (1080p) size, in fullscreen mode
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.FULLSCREEN)
#set up a clock to use later to set the framerate
clock = pygame.time.Clock()
#variable to keep track of if the game is running
game_running = True

#set up a variable to keep track of the current scene, and a function to change it.
"""
My rationale for this is that, by creating a function used for changing the scene,
it allows me to easily pass this function into scene classes, letting me easily transition between scenes from within class code.
I had to wrap the scene variable in a list, to allow for functions to mutate it.
"""
def change_scene(new_scene):
    """
    Changes the main function's current scene

    Parameters
    ----------
    new_scene:
        The new scene to display. Must have an `.update` and `.render` method.
    """
    current_scene[0] = new_scene
current_scene = [MainMenu(screen, change_scene)]

#main gameloop
while game_running:
    pygame.event.get() #TODO: remove this/find an alternative, was only for making sure the window didn't display "not responding"
    #update the current scene (handle user input, changes, etc)
    current_scene[0].update()
    #render the current scene
    current_scene[0].render()
    #display the new frame to the screen
    pygame.display.flip()
    #set the game to a framerate of 30FPS
    clock.tick(30)