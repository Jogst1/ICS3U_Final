#import various modules
import pygame
from Classes.Puzzles.Puzzle import Puzzle
from Classes.ImageHelper import ImageHelper
from Classes.TextRenderer import TextRenderer
from Classes.Game.Grid import Grid
from Classes.ImageButton import ImageButton
from Classes.Game.IOGraph import IOGraph

#set up some constants
INSTRUCTIONS_POSITION = (1549, 145)
INSTRUCTIONS_SIZE = (353, 575)

class Game():
    """
    The main game scene
    """
    def __init__(self, screen: pygame.Surface, puzzle: Puzzle, change_fn):
        """
        Parameters
        ----------
        screen:
            The Surface to blit to.
        puzzle:
            The puzzle to run.
        change_fn:
            A function that changes the scene when provided with a new one.
        """
        #set up some self variables for use in the class
        self.screen = screen
        self.puzzle = puzzle
        self.images = ImageHelper(screen)
        self.sprite_group = pygame.sprite.Group()

        #set up a textrenderer to display the instructions
        instruction_text = TextRenderer(
            puzzle.instructions,
            (0, 0, 0),
            pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 24),
            pygame.Rect(INSTRUCTIONS_POSITION, INSTRUCTIONS_SIZE)
        )
        self.sprite_group.add(instruction_text)

        t = puzzle.example_testcase
        self.io_graph = IOGraph(
            t.inputs,
            t.inputs2,
            t.expected_outputs,
            t.expected_outputs2
        )
        self.io_graph.rect = 20, 750
        self.sprite_group.add(self.io_graph)


        #initialize a grid instance
        self.grid = Grid(puzzle.example_testcase.inputs, puzzle.example_testcase.inputs2)

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

            #temporary until proper win screen is implemented
            if matches == len(tests):
                print("All tests passed")
            else:
                print("A test failed!")
            
            #reset the grid back to the example testcase
            self.grid.get(0, 2).values = self.puzzle.example_testcase.inputs
            self.grid.get(0, 4).values = self.puzzle.example_testcase.inputs2
            self.grid.reset_sim()

        #finish adding the button
        check_tests_button = ImageButton(self.images.check_tests_button, (1561, 749), check_tests_button_onclick, 1.05)
        self.sprite_group.add(check_tests_button)


        
    def update(self):
        """
        Updates the Game scene, including the Grid, all the buttons, and advancement logic.
        """
        self.grid.update()
        self.sprite_group.update()

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


    def render(self):
        """
        Renders the Grid scene to the screen.
        """
        self.screen.blit(self.images.background, (0, 0))
        self.grid.render()
        for sprite in self.sprite_group: self.screen.blit(sprite.surf, sprite.rect)