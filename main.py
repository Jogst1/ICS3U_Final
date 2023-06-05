"""
ICS3U_Final / Merivale I/O
ICS3U-03
Justin Ogston
A computer-science game based on Shenzhen I/O.
History:
3/29/2023: Program Creation
6/5/2023: Major Rewrite
"""

#import os for disabling pygame welcome message
#https://stackoverflow.com/questions/51464455/how-to-disable-welcome-message-when-importing-pygame
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

#import pygame 
import pygame
#initialize pygame
pygame.init()
pygame.mixer.init()
#i learned how to activate fullscreen mode from this stackoverflow question
#https://stackoverflow.com/questions/31538506/how-do-i-maximize-the-display-screen-in-pygame
SCREEN = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

#import classes
from Util.Assets import get_assets
from Classes.Root import Root
get_assets()

#initialize the root of the game 
Root(None, SCREEN)