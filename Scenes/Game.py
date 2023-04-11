import pygame
from Classes.Puzzles.Puzzle import Puzzle
from Classes.ImageHelper import ImageHelper
from Classes.TextRenderer import TextRenderer
from Classes.Game.Grid import Grid

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
        self.screen = screen
        self.puzzle = puzzle
        self.images = ImageHelper(screen)
        self.sprite_group = pygame.sprite.Group()
        instruction_text = TextRenderer(
            puzzle.instructions,
            (0, 0, 0),
            pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 24),
            pygame.Rect(INSTRUCTIONS_POSITION, INSTRUCTIONS_SIZE)
        )
        self.sprite_group.add(instruction_text)
        self.grid = Grid()
        
    def update(self):
        self.grid.update()
    def render(self):
        self.screen.blit(self.images.background, (0, 0))
        self.grid.render()
        for sprite in self.sprite_group: self.screen.blit(sprite.surf, sprite.rect)