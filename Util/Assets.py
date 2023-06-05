import collections
#learned about pathlib from this page: https://docs.python.org/3/library/pathlib.html
import pathlib
import pygame
#learned about how to use glom and why from this page: https://glom.readthedocs.io/en/latest/
import glom


#taken from https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

Assets = dotdict({})

def get_assets():
    """
    Adds all the applicable assets in the Assets directory to the Assets dictionary, for easy access throughout the project.
    """
    BASE_PATH = pathlib.Path("Assets")
    #store this for convert_alphaing pngs
    DISPLAY = pygame.display.get_surface()

    #set up a queue to facilitate the traversal of the Assets directory
    queue = collections.deque(BASE_PATH.iterdir())

    #traverse through the Assets directory in a manner similar to that of BFS
    while len(queue)>0:
        current = queue.pop()

        #if the current item is a file
        if current.is_file():
            assignValue = None #not yet assigned
            #assign a value to the file based on its file extention
            #text files will be converted into a string, that string being their contents
            if current.suffix == ".txt":
                assignValue = current.read_text()
            #png files will be converted into a pygame surface
            elif current.suffix == ".png":
                assignValue = pygame.image.load(current.as_posix()).convert_alpha(DISPLAY)
            #mp3 files will be converted into a pygame sound
            elif current.suffix == ".mp3":
                assignValue = pygame.mixer.Sound(current.as_posix())

            #if the file has a supported filetype
            if assignValue != None:
                #include the file in the Assets dictionary
                #i'm using glom here to massively simplify the assignment
                glom.assign(Assets, current.as_posix().replace("/", ".")[7:], assignValue, dotdict)
        #if the current item is a folder/directory
        elif current.is_dir():
            #skip over music and fonts since we don't want those included in the assets dict
            #don't want music since I use the mixer_music library for that, 
            #and dont want fonts since I import those manually due to wanting multiple different sizes of font
            if current.name == "Music" or current.name == "Fonts": continue
            #add all the dictionary's children to the queue
            queue.extendleft(current.iterdir())
