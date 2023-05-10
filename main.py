#import os and disable pygame welcome message
#https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

#import and initialize pygame
import pygame
pygame.init()

#ensure all music is downloaded: if not, download it
import Assets.Music.get_music as MusicHandler
if not MusicHandler.is_downloaded():
    print("Warning! Music was not initially downloaded. Starting downloads now...")
    print("Note: You will need FFmpeg installed in order for this process to work.")

    MusicHandler.download()

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
#variable to keep track of if the volume slider open
volume_open = True
#variable for debouncing button clicks for the volume control
volume_debounce = False

#load the volume icon, and scale it down
VOLUME_ICON = pygame.transform.smoothscale(pygame.image.load("Assets/volume_icon.png").convert_alpha(screen), (25, 25))
VOLUME_ICON.fill((25, 25, 25), special_flags = pygame.BLEND_MAX)
VOLUME_ADJUST_RECT = pygame.Rect(0, 25, 35, 150)

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
    #update the current scene (handle user input, changes, etc)
    current_scene[0].update()
    #render the current scene
    current_scene[0].render()
    #display the new frame to the screen

    #handle the volume slider. this should be present for all scenes, and so will just be  handled here
    mpos = pygame.mouse.get_pos()
    mb1p = pygame.mouse.get_pressed()[0]

    if mb1p:
        if VOLUME_ICON.get_rect().collidepoint(*mpos) and (not volume_debounce):
            volume_open = not volume_open
        volume_debounce = True
    else:
        volume_debounce = False

    if volume_open:
        pygame.draw.line(screen, (25, 25, 25), (11, 25), (11, 25+100), 10)
        vol = pygame.mixer_music.get_volume()
        pygame.draw.line(screen, (100, 149, 237), (3, 125-(100*vol)), (20, 125-(100*vol)), 3)

        if mb1p:
            if VOLUME_ADJUST_RECT.collidepoint(*mpos):
                print((125-mpos[1])/100)
                pygame.mixer_music.set_volume(max(0, (125-mpos[1])/100))
    

    screen.blit(VOLUME_ICON, VOLUME_ICON.get_rect())

    pygame.display.flip()
    #set the game to a framerate of 30FPS
    clock.tick(30)