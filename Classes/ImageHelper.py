import pygame
import inspect
import os

class ImageHelper():
    """
    A general purpose class for aiding in importing images.
    Imports and `.convert_alpha`s any `.png` files found in the Assets/(ClassName)/ folder, and makes them accessible by using dot notation followed by the image's name

    Example
    -------
    Suppose there is a directory Assets/Example/, which contains two files, example.png, and example.txt
    This class is then initialzed from inside a method of a class named Example, and the result of the initialization is set to a variable named `images`.
    example.png is now accessible by accessing `images.example`. Note that example.txt is not.
    """
    def __init__(self, screen: pygame.Surface):
        """
        screen:
            A surface object used in `.convert_alpha` calls.
        """
        #Line taken and modified from https://stackoverflow.com/a/17065634
        #Determines the name of the calling class
        calling_class_name = inspect.stack()[1][0].f_locals["self"].__class__.__name__

        #scan the Assets/(class name) directory
        directory = os.scandir("Assets/"+calling_class_name)
        #iterate over the items in that directory
        for item in directory:
            #if the item is a .png file
            if item.is_file() and item.name.endswith(".png"):
                #add it to the self.__dict__ object (with the .png string removed from the key)
                #this makes it accessible with dot notation, allowing you to say, access an image named Image.png by writing self.Image
                self.__dict__[item.name[:-4]] = pygame.image.load("Assets/"+calling_class_name+"/"+item.name).convert_alpha(screen)