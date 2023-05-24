#import various modules
import pygame
import pygame.gfxdraw
from math import *
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

#taken from https://stackoverflow.com/questions/68522726/how-to-set-alpha-transparency-property-using-pygame-draw-line
def aaline(surface, color, start_pos, end_pos, width=1):
    """ Draws wide transparent anti-aliased lines. """
    # ref https://stackoverflow.com/a/30599392/355230

    x0, y0 = start_pos
    x1, y1 = end_pos
    midpnt_x, midpnt_y = (x0+x1)/2, (y0+y1)/2  # Center of line segment.
    length = hypot(x1-x0, y1-y0)
    angle = atan2(y0-y1, x0-x1)  # Slope of line.
    width2, length2 = width/2, length/2
    sin_ang, cos_ang = sin(angle), cos(angle)

    width2_sin_ang  = width2*sin_ang
    width2_cos_ang  = width2*cos_ang
    length2_sin_ang = length2*sin_ang
    length2_cos_ang = length2*cos_ang

    # Calculate box ends.
    ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang  + length2_sin_ang)
    ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang  - length2_sin_ang)
    bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang  + length2_sin_ang)
    br = (midpnt_x - length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang  - length2_sin_ang)

    pygame.gfxdraw.aapolygon(surface, (ul, ur, br, bl), color)
    pygame.gfxdraw.filled_polygon(surface, (ul, ur, br, bl), color)

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
        self.checking = False

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
            #if advancing, or the winlose screen is open, the button should do nothing
            if self.advancing or self.status != Status.Playing: return

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
            # if winlose screen is open, disable button
            if self.status != Status.Playing: return

            self.advancing = not self.advancing
            if self.advancing == False:
                self.advcounter = 0
        advance_button = ImageButton(self.images.advance_button, (1682, 856), advance_button_onclick, 1.05)
        self.sprite_group.add(advance_button)


        #set up the button to reset the simulation
        def reset_button_onclick():
            # if winlose screen is open, disable button
            if self.status != Status.Playing: return

            self.advancing = False
            self.advcounter = 0
            self.grid.reset_sim()
            self.io_graph.reset()
        reset_button = ImageButton(self.images.reset_button, (1802, 856), reset_button_onclick, 1.05)
        self.sprite_group.add(reset_button)

        #set up the button to check tests 
        def check_tests_button_onclick():
            #enable checking flag, if already enabled then do not continue
            if self.checking: return
            self.checking = True

            #if winlose screen is open, disable button (if winlose screen is open the current sol'n has been checked)
            if self.status != Status.Playing: return

            #disable advancement
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
                pygame.mixer.Sound("Assets/Sounds/solve.mp3").play()
            elif self.status == Status.Lose:
                pygame.mixer.Sound("Assets/Sounds/solve.mp3").play()
            
            #reset the grid back to the example testcase
            self.grid.get(0, 2).values = self.puzzle.example_testcase.inputs
            self.grid.get(0, 4).values = self.puzzle.example_testcase.inputs2
            self.grid.reset_sim()
            self.io_graph.reset()

            self.checking = False

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

        #if advancing, draw a cross over step button to indicate it is disabled
        if self.advancing:
            pygame.draw.line(self.screen, (163, 49, 35), (1561-5, 856-5), (1561+95, 856+95), 8)
            pygame.draw.line(self.screen, (163, 49, 35), (1561+95, 856-5), (1561-5, 856+95), 8)


        if self.status != Status.Playing:
            self.screen.blit(
                self.images.win_screen if self.status == Status.Win else self.images.fail_screen,
                (710, 240)
            )
            for btn in self.win_lose_buttons:
                self.screen.blit(btn.surf, btn.rect)

            
            #draw a cross over all buttons to indicate they are disabled
            for btnX in [1561, 1682, 1802]:
                pygame.draw.line(self.screen, (163, 49, 35), (btnX-5, 856-5), (btnX+95, 856+95), 8)
                pygame.draw.line(self.screen, (163, 49, 35), (btnX+95, 856-5), (btnX-5, 856+95), 8)
            #checktests
            aaline(self.screen, (163, 49, 35), (1561-10, 749-3), (1561+329+10, 749+97+3), 8)
            aaline(self.screen, (163, 49, 35), (1561-10, 749+97+3), (1561+329+10, 749-3), 8)