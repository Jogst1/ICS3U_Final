#import various modules
import pygame
from enum import Enum
from puzzles import puzzles
from Classes.Puzzles.Puzzle import Puzzle
from Classes.ImageHelper import ImageHelper
from Classes.TextRenderer import TextRenderer
from Classes.Game.Grid import Grid
from Classes.ImageButton import ImageButton
from Classes.Game.IOGraph import IOGraph

#set up some constants
INSTRUCTIONS_POSITION = (1549, 145)
INSTRUCTIONS_SIZE = (353, 575)

class Status(Enum):
    Win=1
    Lose=2
    Playing=3

class Game():
    """
    The main game scene
    """
    def __init__(self, screen: pygame.Surface, puzzleIdx: int, change_fn):
        """
        Parameters
        ----------
        screen:
            The Surface to blit to.
        puzzleIdx:
            The index of the puzzle to run.
        change_fn:
            A function that changes the scene when provided with a new one.
        """

        #play music
        pygame.mixer_music.load(f"Assets/Music/game_{puzzleIdx+1}.mp3")
        pygame.mixer_music.play(-1)

        #set up some self variables for use in the class
        self.screen = screen
        self.change_fn = change_fn
        self.puzzle = puzzles[puzzleIdx]
        self.puzzleIndex = puzzleIdx
        self.images = ImageHelper(screen)
        self.sprite_group = pygame.sprite.Group()
        self.status = Status.Playing

        self.win_lose_buttons = [None, None]

        #set up a textrenderer to display the instructions
        instruction_text = TextRenderer(
            self.puzzle.instructions,
            (0, 0, 0),
            pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 24),
            pygame.Rect(INSTRUCTIONS_POSITION, INSTRUCTIONS_SIZE)
        )
        self.sprite_group.add(instruction_text)

        self.io_graph = IOGraph(
            (t:=self.puzzle.example_testcase).inputs,
            t.inputs2,
            t.expected_outputs,
            t.expected_outputs2
        )
        self.io_graph.rect = 20, 750
        self.sprite_group.add(self.io_graph)


        #initialize a grid instance
        self.grid = Grid(self.puzzle.example_testcase.inputs, self.puzzle.example_testcase.inputs2)

        #set up some variables to keep track of when the advance button is being used
        self.advancing = False
        self.advcounter = 0

        #set up the step button, to advance the sim by one tick
        def step_button_onclick():
            self.grid.do_sim_tick()
            self.io_graph.add_actual(
                self.grid.get(14, 2).output_value,
                self.grid.get(14, 4).output_value
            )
        step_button = ImageButton(self.images.step_button, (1561, 856), step_button_onclick, 1.05)
        self.sprite_group.add(step_button)

        #set up the quit button
        def quit_button_onclick():
            #TODO: Replace this with an actual quit screen
            print("Thank you for playing Merivale I/O!")
            exit()
        quit_button = ImageButton(self.images.quit_button, (1554, 953), quit_button_onclick, 1.05)
        self.sprite_group.add(quit_button)


        #set up the advance button, to repeatedly tick the simulation
        def advance_button_onclick():
            self.advancing = not self.advancing
            if self.advancing == False:
                self.advcounter = 0
        advance_button = ImageButton(self.images.advance_button, (1682, 856), advance_button_onclick, 1.05)
        self.sprite_group.add(advance_button)


        #set up the button to reset the simulation
        def reset_button_onclick():
            self.advancing = False
            self.advcounter = 0
            self.grid.reset_sim()
            self.io_graph.reset()
        reset_button = ImageButton(self.images.reset_button, (1802, 856), reset_button_onclick, 1.05)
        self.sprite_group.add(reset_button)

        #set up the button to check tests 
        def check_tests_button_onclick():
            #first, disable advancement
            self.advancing = False
            self.advcounter = 0

            #set up vars to track all the tests, and the number of perfect matches (passes) the user's solution has gained
            tests = [self.puzzle.example_testcase, *self.puzzle.testcases]
            matches = 0
            #loop over tests
            for test in tests:
                #reset the current grid sim
                self.grid.reset_sim()
                #configure the input IOPorts to have the correct inputs pertaining to the current test
                self.grid.get(0, 2).values = test.inputs
                self.grid.get(0, 4).values = test.inputs2

                output_match_count = 0

                #loop over each expected output for both output IOPorts
                for out1, out2 in zip(test.expected_outputs, test.expected_outputs2):
                    #do a tick
                    self.grid.do_sim_tick()
                    #if both output ports match the expected output then...
                    if out1 == self.grid.get(14, 2).output_value and out2 == self.grid.get(14, 4).output_value:
                        #increment tthe match counter
                        output_match_count += 1

                #if all values matched, increment the number of passed testcases
                matches += int(output_match_count == len(test.expected_outputs))

            self.status = Status(int(matches!=len(tests))+1)
            if self.status == Status.Win:
                pygame.mixer.Sound("Assets/Sounds/solve.wav").play()
            elif self.status == Status.Lose:
                pygame.mixer.Sound("Assets/Sounds/solve.wav").play()
            
            #reset the grid back to the example testcase
            self.grid.get(0, 2).values = self.puzzle.example_testcase.inputs
            self.grid.get(0, 4).values = self.puzzle.example_testcase.inputs2
            self.grid.reset_sim()
            self.io_graph.reset()

        #finish adding the button
        check_tests_button = ImageButton(self.images.check_tests_button, (1561, 749), check_tests_button_onclick, 1.05)
        self.sprite_group.add(check_tests_button)


        
    def update(self):
        """
        Updates the Game scene, including the Grid, all the buttons, and advancement logic.
        """
        self.grid.update()
        self.sprite_group.update()
        for btn in self.win_lose_buttons:
            if btn != None:
                btn.update()

        if self.advancing:
            if self.advcounter == 0:
                if self.grid.get(0, 2).value_index == len(self.grid.get(0, 2).values) - 1:
                    self.advancing = False
                    self.advcounter = 0
                self.grid.do_sim_tick()
                self.io_graph.add_actual(
                    self.grid.get(14, 2).output_value,
                    self.grid.get(14, 4).output_value
                )
            self.advcounter = (self.advcounter + 1) % 15


        if self.win_lose_buttons[0] == None:
            if self.status == Status.Win:
                def next_level_onclick():
                    if self.puzzleIndex+1 == len(puzzles):
                        #TODO: proper end game screen
                        print("You finished all the puzzles! You win!")
                        exit()
                    else:
                        self.change_fn(Game(self.screen, self.puzzleIndex+1, self.change_fn))

                self.win_lose_buttons[0] = ImageButton(
                    self.images.next_level_button,
                    (730, 622),
                    next_level_onclick,
                    1.05
                )

                def keep_playing_onclick():
                    self.status = Status.Playing

                self.win_lose_buttons[1] = ImageButton(
                    self.images.keep_playing_button,
                    (730, 723),
                    keep_playing_onclick,
                    1.05
                )
            elif self.status == Status.Lose:
                def try_again_onclick():
                    self.status = Status.Playing

                self.win_lose_buttons[0] = ImageButton(
                    self.images.try_again_button,
                    (730, 622),
                    try_again_onclick,
                    1.05
                )

                def quit_game_onclick():
                    print("Thank you for playing Merivale I/O")
                    exit()

                self.win_lose_buttons[1] = ImageButton(
                    self.images.fail_quit_button,
                    (730, 723),
                    quit_game_onclick,
                    1.05
                )
        if self.status == Status.Playing:
            self.win_lose_buttons = [None, None]


    def render(self):
        """
        Renders the Grid scene to the screen.
        """
        self.screen.blit(self.images.background, (0, 0))
        self.grid.render()
        for sprite in self.sprite_group: self.screen.blit(sprite.surf, sprite.rect)

        if self.status != Status.Playing:
            self.screen.blit(
                self.images.win_screen if self.status == Status.Win else self.images.fail_screen,
                (710, 240)
            )
            for btn in self.win_lose_buttons:
                self.screen.blit(btn.surf, btn.rect)