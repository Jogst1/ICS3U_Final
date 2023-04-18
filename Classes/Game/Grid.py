import pygame
from math import floor
from collections import deque
from Classes.Game.Microcontroller import Microcontroller, MicroPointer
from Classes.Game.Wire import Wire, WireNeighbors as Neighbors
from Classes.Game.IOPort import IOPort

GRID_SIZE = (15, 7)
PLACE_MICROCONTROLLER_KEY = pygame.K_e
REMOVE_MICROCONTROLLER_KEY = pygame.K_q
GRID_SIZE_PIXELS = (1500, 700)
GRID_POSITION = (20, 20)
MICROCONTROLLER_OFFSET = 10

class Grid(pygame.sprite.Sprite):
    """
    Represents the grid where wires and microcontrollers will be placed.
    """

    def __init__(self, input1values, input2values):
        self.grid = {(x, y): None for x in range(GRID_SIZE[0]) for y in range(GRID_SIZE[1])}
        self.screen = pygame.display.get_surface()

        self.grid[(0, 2)] = IOPort("Input 1", input1values)
        self.grid[(0, 2)].rect.topleft = (40, 240)

        self.grid[(0, 4)] = IOPort("Input 2", input2values)
        self.grid[(0, 4)].rect.topleft = (40, 440)

        self.grid[(14, 2)] = IOPort("Output 1")
        self.grid[(14, 2)].rect.topleft = (1440, 240)

        self.grid[(14, 4)] = IOPort("Output 2")
        self.grid[(14, 4)].rect.topleft = (1440, 440)
    
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

        update_sprites = [item for item in self.grid.values() if issubclass(type(item), pygame.sprite.Sprite)]
        for sprite in update_sprites: 
            if isinstance(sprite, Microcontroller):
                sprite.update(events)
            else:
                sprite.update()

    def render(self):
        render_sprites = [item for item in self.grid.values() if issubclass(type(item), pygame.sprite.Sprite)]
        for sprite in render_sprites:
            self.screen.blit(sprite.surf, sprite.rect)

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

    def add_microcontroller(self, center_position):
        #make sure the micro wouldnt clip out of the grid
        if (
            center_position[0] == GRID_SIZE[0]-1 or
            center_position[0] == 0 or 
            center_position[1] == GRID_SIZE[1]-1
        ): return

        #make sure micro wont overlap IOPorts or another micro
        for item in [self.get(*center_position, mod) for mod in [
            (0, 0),
            (-1, 0),
            (-1, 1),
            (1, 0),
            (1, 1),
            (0, 1)
        ]]:
            if isinstance(item, (IOPort, Microcontroller, MicroPointer)): return

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

        #stop deletion if micro is being typed in
        micro = self.get(*microcontroller_pos)
        if micro.typing:
            return

        for modifier in [
            (0, 0),
            (-1, 0),
            (-1, 1),
            (1, 0),
            (1, 1),
            (0, 1)
        ]:
            self.grid[(microcontroller_pos[0] + modifier[0], microcontroller_pos[1] + modifier[1])] = None

    

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
            elif isinstance(neighbor, IOPort):
                boolNeighbors.append(True)
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

    def do_sim_tick(self):
        for ioportpos in [(0, 2), (0, 4), (14, 2), (14, 4)]:
            ioport = self.get(*ioportpos)
            ioport.do_sim_tick()
            ioport.update_surf()

        #perform a breadth-first traversal of the wire networks starting from input nodes, ending at microcontroller ports
        visited = [(0, 2), (0, 4)]
        queue = deque(visited.copy())

        while len(queue) > 0:
            current = queue.pop()
            current_instance = self.get(*current)
            c_val = current_instance.value if isinstance(current_instance, Wire) else current_instance.values[current_instance.value_index]

            neighbors = [
                pos
                for mod in [
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1)
                ]
                if self.get(*(pos := (current[0] + mod[0], current[1] + mod[1]))) != None
                and pos not in visited
            ]

            for neighbor in neighbors:
                neighbor_instance = self.get(*neighbor)

                if isinstance(neighbor_instance, Wire):
                    neighbor_instance.value = c_val
                    neighbor_instance.update_surf()
                    queue.appendleft(neighbor)
                elif isinstance(neighbor_instance, IOPort):
                    if neighbor_instance.is_output_port():
                        neighbor_instance.output_value = c_val
                elif isinstance(neighbor_instance, MicroPointer):
                    if neighbor_instance.portId != None:
                        if "in" in neighbor_instance.portId:
                            micro = self.get(*neighbor_instance.pointTo)
                            micro.__dict__[neighbor_instance.portId] = c_val

                visited.append(neighbor)
        
        #do a simulation tick on all microcontrollers
        for micro in [m for m in self.grid.values() if isinstance(m, Microcontroller)]:
            micro.do_sim_tick()

        #get a list of all the output ports for every microcontroller
        visited = [
            item for sublist in 
            [
                [(pos[0]-1, pos[1]+1), (pos[0]+1, pos[1])] 
                for pos in self.grid.keys() 
                if isinstance(self.get(*pos), Microcontroller)
            ] 
            for item in sublist
        ]
        queue = deque(visited.copy())

        #do another bfs to propagate output values from the microcontroller simulation tick
        while len(queue) > 0:
            current = queue.pop()
            current_instance = self.get(*current)
            c_val = current_instance.value if isinstance(current_instance, Wire) else self.get(*current_instance.pointTo).__dict__[current_instance.portId]

            neighbors = [
                pos
                for mod in [
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1)
                ]
                if self.get(*(pos := (current[0] + mod[0], current[1] + mod[1]))) != None
                and pos not in visited
            ]

            #if the current instance is a micropointer, prevent it from adding other micropointers to the neighbor list 
            if isinstance(current_instance, MicroPointer):
                neighbors = [neighbor for neighbor in neighbors if not isinstance(self.get(*neighbor), MicroPointer)]

            for neighbor in neighbors:
                neighbor_instance = self.get(*neighbor)

                if isinstance(neighbor_instance, Wire):
                    neighbor_instance.value = c_val
                    neighbor_instance.update_surf()
                    queue.appendleft(neighbor)
                elif isinstance(neighbor_instance, IOPort):
                    if neighbor_instance.is_output_port():
                        neighbor_instance.output_value = c_val
                elif isinstance(neighbor_instance, MicroPointer):
                    if neighbor_instance.portId != None:
                        if "in" in neighbor_instance.portId:
                            micro = self.get(*neighbor_instance.pointTo)
                            micro.__dict__[neighbor_instance.portId] = c_val

                visited.append(neighbor)

        