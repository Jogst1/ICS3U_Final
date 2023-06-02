import pygame
from Classes.Instance import Instance
from Classes.ImageButton import ImageButton
from Util.Assets import Assets
from Classes.Scenes.Credits import Credits
from Classes.Scenes.Tutorial import Tutorial

class MainMenu(Instance):
    """
    The main menu scene for the game
    """
    def __init__(self, parent: Instance):
        super().__init__(parent)

        #play music
        pygame.mixer_music.load("Assets/Music/main_menu.mp3")
        pygame.mixer_music.play(-1, 1.5)

        #set up the background
        self.renderables["background"] = (
            Assets.MainMenu.background.png,
            3
        )

        #set up some buttons
        def start_button_onclick():
            self.parent.add_child("tutorial_scene", Tutorial(self.parent))
            self.parent.remove_child("main_menu_scene")
        self.add_child("start_button", ImageButton(
            self,
            Assets.MainMenu.start_button.png,
            start_button_onclick,
            (526, 452),
            1.05,
            2
        ))

        def credits_button_onclick():
            self.parent.add_child("credits_scene", Credits(self.parent))
            self.parent.remove_child("main_menu_scene")
        self.add_child("credits_button", ImageButton(
            self,
            Assets.MainMenu.credits_button.png,
            credits_button_onclick,
            (489, 676),
            1.05,
            2
        ))