import pygame
from enum import Enum
from Classes.Instance import Instance, MouseState
from Classes.TextRenderer import TextRenderer
from Classes.ImageButton import ImageButton, Cross
from Util.Assets import Assets
from puzzles import puzzles

from Classes.Game.Grid import Grid
from Classes.Game.IOGraph import IOGraph

INSTRUCTIONS_POSITION = (1549, 145)
INSTRUCTIONS_SIZE = (353, 575)

#i learned about enums from here:
#https://docs.python.org/3/library/enum.html#enum.Enum
#had the idea to use them and search for the specific term due to my experience with rust
class Status(Enum):
    """
    Represents the state of a puzzle, can be the win or lose state, or still playing state
    """
    Win=1
    Lose=2
    Playing=3

class Game(Instance):
    """
    Represents a puzzle level in the game.
    """
    def __init__(self, parent: Instance, puzzleId: int):
        super().__init__(parent)

        #play music
        pygame.mixer_music.load(f"Assets/Music/game_{puzzleId+1}.mp3")
        pygame.mixer_music.play(-1)

        #keep track of actual puzzle object
        self.puzzle = puzzles[puzzleId]
        #keep track of puzzleid, will need it outside of init fn
        self.puzzleId = puzzleId
        #keep track of status for obvious reasons
        self.status = Status.Playing
        #flag to determine if game is checking for pass on testcase
        self.checking = False

        self.renderables["background"] = (
            Assets.Game.background.png,
            5
        )

        #set up instructions text
        self.add_child("instructions", TextRenderer(
            self,
            self.puzzle.instructions,
            (0, 0, 0),
            pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 24),
            pygame.Rect(INSTRUCTIONS_POSITION, INSTRUCTIONS_SIZE)
        ))

        #add grid
        self.add_child("grid", Grid(self))
        #add iograph
        self.add_child("iograph", IOGraph(self))

        #a couple attributes for advancing logic
        self.advancing = False
        self.advance_timer = 0

        #add buttons
        def step_button_onclick():
            if len(self.children["iograph"].actual1) == self.children["iograph"].LENGTH: return
            if self.advancing or self.status != Status.Playing: return

            self.children["grid"].tick()
            self.children["iograph"].add_actual(
                self.children["grid"].get(14, 2).output_value,
                self.children["grid"].get(14, 4).output_value,
            )
        self.add_child(
            "step_button",
            ImageButton(self, Assets.Game.step_button.png, step_button_onclick, (1561, 856), 1.05)
        )

        def advance_button_onclick():
            if self.status != Status.Playing: return

            self.advancing = not self.advancing
            if not self.advancing: 
                self.advance_timerer = 0
            self.update_win_lose_screen()
            
        self.add_child(
            "advance_button",
            ImageButton(self, Assets.Game.advance_button.png, advance_button_onclick, (1682, 856), 1.05)
        )

        def reset_button_onclick():
            if self.status != Status.Playing: return

            self.advancing = False
            self.advance_timer = 0

            self.children["grid"].reset()
            self.children["iograph"].reset()

            self.update_win_lose_screen()

        self.add_child(
            "reset_button",
            ImageButton(self, Assets.Game.reset_button.png, reset_button_onclick, (1802, 856), 1.05)
        )

        def check_button_onclick():
            if self.checking: return
            self.checking = True

            #disable button if a winlose screen is already open
            if self.status != Status.Playing: return

            #disable advancement
            self.advance_timer = 0 
            self.advancing = False

            results = []

            #get a list of all testcases in the puzzle
            tests = [self.puzzle.example_testcase, *self.puzzle.testcases]
            for test in tests:
                #reset the current grid sim
                self.children["grid"].reset()
                #configure the input IOPorts to have the correct inputs pertaining to the current test
                self.children["grid"].get(0, 2).values = test.inputs
                self.children["grid"].get(0, 4).values = test.inputs2

                subresults = []
                
                for out1, out2 in zip(test.expected_outputs, test.expected_outputs2):
                    self.children["grid"].tick()
                    subresults.append(
                        out1 == self.children["grid"].get(14, 2).output_value and
                        out2 == self.children["grid"].get(14, 4).output_value
                    )

                results.append(all(subresults))

            #set status
            win = all(results)
            self.status = Status.Win if win else Status.Lose
            self.update_win_lose_screen()

            #play sfx
            pygame.mixer.Sound("Assets/Sounds/solve.mp3").play()

            #reset the grid back to the example testcase
            self.children["grid"].get(0, 2).values = self.puzzle.example_testcase.inputs
            self.children["grid"].get(0, 4).values = self.puzzle.example_testcase.inputs2
            self.children["grid"].reset()
            self.children["iograph"].reset()   

            self.checking = False

        self.add_child(
            "check_button",
            ImageButton(
                self,
                Assets.Game.check_tests_button.png,
                check_button_onclick,
                (1561, 749),
                1.05,
                1
            )
        )



    def update(self, events: list[pygame.event.Event], mouseState: MouseState, deltaTime: float):
        if self.advancing:
            if self.advance_timer > 0.5:
                self.advance_timer = 0
                if self.children["grid"].get(0, 2).value_index == len(self.children["grid"].get(0, 2).values) - 1:
                    self.advancing = False
                    self.advance_timer = 0
                    self.update_win_lose_screen()
                self.children["grid"].tick()
                self.children["iograph"].add_actual(
                    self.children["grid"].get(14, 2).output_value,
                    self.children["grid"].get(14, 4).output_value
                )
            self.advance_timer = self.advance_timer + deltaTime

    def update_win_lose_screen(self):
        if self.status == Status.Playing:
            if self.advancing:
                self.children["step_button"].add_child(
                    "cross",
                    Cross(
                        self.children["step_button"]
                    )
                )
            else:
                self.children["step_button"].remove_child("cross")
            for key in [
                "advance",
                "reset",
                "check"
            ]:
                self.children[f"{key}_button"].remove_child("cross")

            if "win_screen" in self.renderables:
                del self.renderables["win_screen"]
                self.remove_child("next_button")
                self.remove_child("keep_button")
                if "text_overwrite" in self.renderables:
                    del self.renderables["text_overwrite"]

            if "lose_screen" in self.renderables:
                del self.renderables["lose_screen"]
                self.remove_child("again_button")
        elif self.status == Status.Win:
            for key in [
                "advance",
                "reset",
                "check",
                "step"
            ]:
                self.children[f"{key}_button"].add_child(
                    "cross",
                    Cross(
                        self.children[f"{key}_button"]
                    )
                )
            self.renderables["win_screen"] = (
                (
                    Assets.Game.win_screen.png,
                    Assets.Game.win_screen.png.get_rect(
                        topleft = (710, 240)
                    )
                ),
                -1
            )
            if self.puzzleId+1 < len(puzzles):
                def next_onclick():
                    self.parent.add_child(
                        f"game_scene_{self.puzzleId+1}",
                        Game(
                            self.parent,
                            self.puzzleId+1
                        )
                    )
                    self.parent.remove_child(f"game_scene_{self.puzzleId}")
                self.add_child(
                    "next_button",
                    ImageButton(
                        self,
                        Assets.Game.next_level_button.png,
                        next_onclick,
                        (730, 622),
                        1.05,
                        -2
                    )
                )
            else:
                self.renderables["text_overwrite"] = (
                    (Assets.Game.text_overwrite.png,
                    Assets.Game.text_overwrite.png.get_rect(
                        topleft = (
                            730,
                            425
                        )
                    )),
                    -1
                )
            def keep_onclick():
                self.status = Status.Playing
                self.update_win_lose_screen()
            self.add_child(
                "keep_button",
                ImageButton(
                    self,
                    Assets.Game.keep_playing_button.png,
                    keep_onclick,
                    (730, (723 if self.puzzleId+1 < len(puzzles) else 672)),
                    1.05,
                    -2
                )
            )
        elif self.status == Status.Lose:
            for key in [
                "advance",
                "reset",
                "check",
                "step"
            ]:
                self.children[f"{key}_button"].add_child(
                    "cross",
                    Cross(
                        self.children[f"{key}_button"]
                    )
                )
            
            self.renderables["lose_screen"] = (
                (
                    Assets.Game.fail_screen.png,
                    Assets.Game.fail_screen.png.get_rect(
                        topleft = (710, 240)
                    )
                ),
                -1
            )
            def again_onclick():
                self.status = Status.Playing
                self.update_win_lose_screen()
            self.add_child(
                "again_button",
                ImageButton(
                    self,
                    Assets.Game.try_again_button.png,
                    again_onclick,
                    (730, 672),
                    1.05,
                    -2
                )
            )