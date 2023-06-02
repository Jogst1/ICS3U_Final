import collections
import pathlib
import pygame
import glom


#taken from https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

Assets = dotdict({})

def get_assets():
    BASE_PATH = pathlib.Path("Assets")
    DISPLAY = pygame.display.get_surface()

    queue = collections.deque(BASE_PATH.iterdir())

    while len(queue)>0:
        current = queue.pop()

        if current.is_file():
            assignValue = None #not yet assigned
            if current.suffix == ".txt":
                assignValue = current.read_text()
            elif current.suffix == ".png":
                assignValue = pygame.image.load(current.as_posix()).convert_alpha(DISPLAY)
            elif current.suffix == ".mp3":
                assignValue = pygame.mixer.Sound(current.as_posix())

            if assignValue != None:
                glom.assign(Assets, current.as_posix().replace("/", ".")[7:], assignValue, dotdict)
            


        elif current.is_dir():
            if current.name == "Music" or current.name == "Fonts": continue
            queue.extendleft(current.iterdir())
