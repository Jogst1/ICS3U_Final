import pygame
from Classes.ImageButton import ImageButton
from Classes.Instance import Instance, MouseState
from Classes.TextRenderer import TextRenderer
from Util.Assets import Assets

class Credits(Instance):
    """
    The Credits scene, which displays text detailing various credits about the game.
    """

    def __init__(self, parent: Instance):
        super().__init__(parent)

        from Classes.Scenes.MainMenu import MainMenu

        #play music
        pygame.mixer_music.load("Assets/Music/text_screen.mp3")
        pygame.mixer_music.play(-1, 4)

        #get a list of pages
        self.pages = Assets.Credits.credits.txt.split("<NEWPAGE>")
        #keep track of the current page the user is on
        self.page_index = 0

        #set up the background
        self.renderables["background"] = (
            Assets.Credits.background.png,
            2
        )

        #set up the text renderer
        self.add_child("text", TextRenderer(
            self,
            self.pages[self.page_index],
            (0, 0, 0),
            pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 30),
            pygame.Rect((518, 278), (884, 525)),
        ))

        #set up some buttons. storing some of these as attributes since theyre gonna be conditionally rendered

        def upd_visible_buttons():
            #conditionally enable the backforward buttons
            if self.page_index != 0 and "back_button" not in self.children:
                self.add_child("back_button", self.back_button)
            if self.page_index != len(self.pages)-1 and "next_button" not in self.children:
                self.add_child("next_button", self.next_button)

            if self.page_index == 0:
                self.remove_child("back_button")

            if self.page_index == len(self.pages) - 1:
                self.remove_child("next_button")

            

        def back_button_onclick():
            self.page_index -= 1
            self.children["text"].set_text(self.pages[self.page_index])
            upd_visible_buttons()
        self.back_button = ImageButton(
            self,
            Assets.Credits.back_button.png,
            back_button_onclick,
            (410, 865),
            1.05,
            1
        )
        def next_button_onclick():
            self.page_index += 1
            self.children["text"].set_text(self.pages[self.page_index])
            upd_visible_buttons()
        self.next_button = ImageButton(
            self,
            Assets.Credits.next_button.png,
            next_button_onclick,
            (1150, 865),
            1.05,
            1
        )
        def close_button_onclick():
            self.parent.add_child("main_menu_scene", MainMenu(
                self.parent
            ))
            self.parent.remove_child("credits_scene")
        self.add_child("close_button", ImageButton(
            self,
            Assets.Credits.close_button.png,
            close_button_onclick,
            (785, 865),
            1.05,
            1
        ))

        upd_visible_buttons()

    def update(self, _: list[pygame.event.Event], mstate: MouseState, ___: float):
        #only update the backbutton if it should be visible (i.e. user isn't on first page)
        if self.page_index != 0:
            self.back_button.update(None, mstate, None)
        #only update the next button if it should be visible (i.e. user isn't on last page)
        if self.page_index != len(self.pages)-1:
            self.next_button.update(None, mstate, None)