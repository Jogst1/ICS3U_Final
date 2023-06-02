#import os for disabling pygame welcome message
#https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

#import pygame 
import pygame
#initialize pygame
pygame.init()
pygame.mixer.init()
SCREEN = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

#import classes
from Util.Assets import get_assets
from Classes.Root import Root
get_assets()

Root(None, SCREEN)