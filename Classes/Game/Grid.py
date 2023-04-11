import pygame
from math import floor
from Classes.Game.Microcontroller import Microcontroller, MicroPointer
from Classes.Game.Wire import Wire, WireNeighbors as Neighbors

GRID_SIZE = (15, 7)
PLACE_MICROCONTROLLER_KEY = pygame.K_e
REMOVE_MICROCONTROLLER_KEY = pygame.K_q
GRID_SIZE_PIXELS = (1500, 700)
GRID_POSITION = (20, 20)
MICROCONTROLLER_OFFSET = 10

class Grid():
    """
    Represents the grid where wires and microcontrollers will be placed.
    """

    def __init__(self):
        self.grid = {(x, y): None for x in range(GRID_SIZE[0]) for y in range(GRID_SIZE[1])}
        self.screen = pygame.display.get_surface()
    
    def update(self):
        events = pygame.event.get()
        
        #check the mouse is in the bounds of the grid
        mouse_position = pygame.mouse.get_pos()
        if (
            mouse_position[0] < GRID_POSITION[0] or
            mouse_position[0] > GRID_POSITION[0] + GRID_SIZE_PIXELS[0] or
            mouse_position[1] < GRID_POSITION[1] or
            mouse_position[1] > GRID_POSITION[1] + GRID_SIZE_PIXELS[1]
        ):
            return
        
        mouse_relative_position = (mouse_position[0] - GRID_POSITION[0], mouse_position[1] - GRID_POSITION[1])
        mouse_grid = (floor(mouse_relative_position[0] / 100), floor(mouse_relative_position[1] / 100))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == PLACE_MICROCONTROLLER_KEY:
                    self.add_microcontroller(mouse_grid)
                elif event.key == REMOVE_MICROCONTROLLER_KEY:
                    self.remove_microcontroller(mouse_grid)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.add_wire(mouse_grid)
                else:
                    self.remove_wire(mouse_grid)

    def render(self):
        render_sprites = [item for item in self.grid.values() if issubclass(type(item), pygame.sprite.Sprite)]
        for sprite in render_sprites: 
            self.screen.blit(sprite.surf, sprite.rect)

    def add_microcontroller(self, center_position):
        #make sure the micro wouldnt clip out of the grid
        if (
            center_position[0] == GRID_SIZE[0]-1 or
            center_position[0] == 0 or 
            center_position[1] == GRID_SIZE[1]-1
        ): return
        self.grid[center_position] = Microcontroller((
            ((center_position[0] - 1) * 100) + GRID_POSITION[0] + MICROCONTROLLER_OFFSET,
            (center_position[1] * 100) + GRID_POSITION[1] + MICROCONTROLLER_OFFSET
        ))

        for modifier in [
            (-1, 0, "in1"),
            (+1, 0, "ou2"),
            (-1, +1, "ou1"),
            (0, +1, None),
            (+1, +1, "ou2")
        ]:
            self.grid[(center_position[0] + modifier[0], center_position[1] + modifier[1])] = MicroPointer(center_position, modifier[2])
            
    def remove_microcontroller(self, position):
        #check that the requested remove location is actually a microcontroller
        if not isinstance(self.grid[position], (Microcontroller, MicroPointer)): return

        microcontroller_pos = position if isinstance(self.grid[position], Microcontroller) else self.grid[position].pointTo

        for modifier in [
            (0, 0),
            (-1, 0),
            (+1, 0),
            (-1, -1),
            (0, -1),
            (+1, -1)
        ]:
            self.grid[(microcontroller_pos[0] + modifier[0], microcontroller_pos[1] + modifier[1])] = None

    def get(self, x, y, change=(0, 0)):
        x += change[0]
        y += change[1]
        if (
            x < 0 or
            x > GRID_SIZE[0] - 1 or
            y < 0 or
            y > GRID_SIZE[1] - 1
        ): return None
        return self.grid[(x, y)]

    def add_wire(self, position):
        if self.grid[position] != None: return

        neighbors = [self.get(*position, m) for m in [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]]

        boolNeighbors = []
        for neighbor, direction in zip(neighbors, [
            "down",
            "up",
            "right",
            "left"
        ]):
            if isinstance(neighbor, Wire):
                boolNeighbors.append(True)
                neighbor_current_neighbors = neighbor.current_neighbors
                neighbor_current_neighbors.__dict__[direction] = True
                neighbor.update_neighbors(neighbor_current_neighbors)
            elif isinstance(neighbor, MicroPointer):
                if direction == "left" or direction == "right":
                    boolNeighbors.append(True)
                else:
                    boolNeighbors.append(False)
            else:
                boolNeighbors.append(False)

        wire = Wire(Neighbors(*boolNeighbors), (
            (position[0] * 100) + GRID_POSITION[0],
            (position[1] * 100) + GRID_POSITION[1]
        ))
        self.grid[position] = wire

    def remove_wire(self, position):
        if not isinstance(self.grid[position], Wire): return
        self.grid[position] = None
        for modifier, direction in zip(
            [  
                (0, -1),
                (0, 1),
                (-1, 0),
                (1, 0)
            ],
            [
                "down",
                "up",
                "right",
                "left"
            ]
        ):
            gotten = self.get(position[0], position[1], modifier)
            if not isinstance(gotten, Wire): continue
            
            wire_current_neighbors = gotten.current_neighbors
            wire_current_neighbors.__dict__[direction] = False
            gotten.update_neighbors(wire_current_neighbors)
