#import modules
import pygame
import typing
from math import floor
from collections import deque
from Classes.Game.Microcontroller import Microcontroller, MicroPointer
from Classes.Game.Wire import Wire, WireNeighbors as Neighbors
from Classes.Game.IOPort import IOPort

#set up some constants for use later
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

    def __init__(self, input1values: list[int], input2values: list[int]):
        """
        Initializes the grid where microcontrollers and wires will be placed.

        Parameters
        ----------
        input1values:
            List of values that IOPort1 should adopt.
        input2values:
            List of values that IOPort2 should adopt
        """
        #set up the actual grid where items will be, using a dictionary comprehension
        #keys will be a tuple (x, y), for ease of programming
        self.grid = {(x, y): None for x in range(GRID_SIZE[0]) for y in range(GRID_SIZE[1])}
        #set up a screen to render things to
        self.screen = pygame.display.get_surface()


        #set up all the IOPorts
        self.grid[(0, 2)] = IOPort("Input 1", input1values)
        self.grid[(0, 2)].rect.topleft = (40, 240)

        self.grid[(0, 4)] = IOPort("Input 2", input2values)
        self.grid[(0, 4)].rect.topleft = (40, 440)

        self.grid[(14, 2)] = IOPort("Output 1")
        self.grid[(14, 2)].rect.topleft = (1440, 240)

        self.grid[(14, 4)] = IOPort("Output 2")
        self.grid[(14, 4)].rect.topleft = (1440, 440)
    
    def update(self):
        """
        Updates the grid, handling things like user input, and sprite updates.
        """

        #get all events
        events = pygame.event.get()
        
        #check the mouse is in the bounds of the grid
        mouse_position = pygame.mouse.get_pos()
        if (
            mouse_position[0] < GRID_POSITION[0] or
            mouse_position[0] > GRID_POSITION[0] + GRID_SIZE_PIXELS[0] or
            mouse_position[1] < GRID_POSITION[1] or
            mouse_position[1] > GRID_POSITION[1] + GRID_SIZE_PIXELS[1]
        ):
            #if it isn't, do nothing.
            return
        
        #get the mouse's relative position (mouse position accounting for grid offset)
        mouse_relative_position = (mouse_position[0] - GRID_POSITION[0], mouse_position[1] - GRID_POSITION[1])
        #get the grid coordinate of the mouse
        mouse_grid = (floor(mouse_relative_position[0] / 100), floor(mouse_relative_position[1] / 100))


        #loop over all events
        for event in events:
            #if event is a keyboard press
            if event.type == pygame.KEYDOWN:
                #if key is to place microcontroller (E)
                if event.key == PLACE_MICROCONTROLLER_KEY:
                    #add the microcontroller at the mouses position
                    self.add_microcontroller(mouse_grid)
                #if key is to remove microcontroller (Q)
                elif event.key == REMOVE_MICROCONTROLLER_KEY:
                    #removve the microcontroller underneath the mouse
                    self.remove_microcontroller(mouse_grid)
            #if event is a mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #if mouseclick is to add wire (mb1)
                if event.button == 1:
                    #add wire at mouse pos
                    self.add_wire(mouse_grid)
                #if it is to remove wire (right click)
                else:
                    #remove wire at mouse pos
                    self.remove_wire(mouse_grid)

        #use a list comp to get all sprites in the grid
        update_sprites = [item for item in self.grid.values() if issubclass(type(item), pygame.sprite.Sprite)]
        #update the sprites, passing the list of events if sprite is microcontroller (this allows typing input)
        for sprite in update_sprites: 
            if isinstance(sprite, Microcontroller):
                sprite.update(events)
            else:
                sprite.update()

    def render(self):
        """
        Renders out the grid items to the screen
        """
        #use a list comp to get all sprites in the grid
        render_sprites = [item for item in self.grid.values() if issubclass(type(item), pygame.sprite.Sprite)]
        #render all sprites to teh screen
        for sprite in render_sprites:
            self.screen.blit(sprite.surf, sprite.rect)

    def get(self, x: int, y: int, change: tuple[int, int]=(0, 0)) -> typing.Any:
        """
        Gets the instance at a given position in the grid, and returns it.
        Returns None if the position is empty, or if the position is out of bounds.
        Supports a change variable for easily modifying the position by a tuple.

        Parameters
        ----------
        x: 
            The x position to look at
        y:
            The y position to look at
        change
            The (x, y) tuple to modify the provided x/y arguments by. Optional, defaults to (0, 0)
        """
        #modify x,y by the change tuple
        x += change[0]
        y += change[1]

        #if location is out of bounds, return None
        if (
            x < 0 or
            x > GRID_SIZE[0] - 1 or
            y < 0 or
            y > GRID_SIZE[1] - 1
        ): return None

        #return the requested value
        return self.grid[(x, y)]

    def add_microcontroller(self, center_position: tuple[int, int]):
        """
        Adds a microcontroller object to the requested position

        Parameters
        ----------
        center_position: 
            The position the microcontroller will be centred on
        """
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

        #instantiate the microcontroller, calculating the pixel coordinate x,y position it should be at
        self.grid[center_position] = Microcontroller((
            ((center_position[0] - 1) * 100) + GRID_POSITION[0] + MICROCONTROLLER_OFFSET,
            (center_position[1] * 100) + GRID_POSITION[1] + MICROCONTROLLER_OFFSET
        ))

        #create MicroPointer instances surrounding the micro
        for modifier in [
            (-1, 0, "in1"),
            (+1, 0, "ou2"),
            (-1, +1, "ou1"),
            (0, +1, None),
            (+1, +1, "ou2")
        ]:
            self.grid[(center_position[0] + modifier[0], center_position[1] + modifier[1])] = MicroPointer(center_position, modifier[2])
            
            
    def remove_microcontroller(self, position: tuple[int, int]):
        """
        Removes a microcontroller from a requested position
        """
        #check that the requested remove location is actually a microcontroller
        if not isinstance(self.grid[position], (Microcontroller, MicroPointer)): return

        microcontroller_pos = position if isinstance(self.grid[position], Microcontroller) else self.grid[position].pointTo

        #stop deletion if micro is being typed in
        micro = self.get(*microcontroller_pos)
        if micro.typing:
            return

        #remove associated micropointer instances
        for modifier in [
            (0, 0),
            (-1, 0),
            (-1, 1),
            (1, 0),
            (1, 1),
            (0, 1)
        ]:
            self.grid[(microcontroller_pos[0] + modifier[0], microcontroller_pos[1] + modifier[1])] = None

    

    def add_wire(self, position: tuple[int, int]):
        """
        Adds a wire in the requested position.
        """

        #ensure the grid position is empty, if it isn't cancel the addition
        if self.grid[position] != None: return


        #get all the wire's neighbors.
        neighbors = [self.get(*position, m) for m in [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]]

        #array to keep track of if a wire has neighbors in a specific direction or not
        boolNeighbors = []

        #loop over the neighbors, zipped with some directioanl strings
        for neighbor, direction in zip(neighbors, [
            "down",
            "up",
            "right",
            "left"
        ]):
            #if the neighbor is a wire
            if isinstance(neighbor, Wire):
                #add a true to the wire's neighbor list
                boolNeighbors.append(True)
                #update the neighbor wire's neighbors, since it's getting a new one with the placed wire
                neighbor_current_neighbors = neighbor.current_neighbors
                neighbor_current_neighbors.__dict__[direction] = True
                neighbor.update_neighbors(neighbor_current_neighbors)
            #if the neighbor is a micropointer
            elif isinstance(neighbor, MicroPointer):
                #if the neighbor is a horizontal one
                if direction == "left" or direction == "right":
                    #add it as a neighbor to the new wire's list
                    boolNeighbors.append(True)
                else:
                    #don't
                    boolNeighbors.append(False)
            #if neighbor is an IOPort
            elif isinstance(neighbor, IOPort):
                #add it as a neighbor to the wire's list
                boolNeighbors.append(True)
            #otherwise
            else:
                #add it as a non-neighbor to the wire's list
                boolNeighbors.append(False)

        #instantiate a new wire, calculating the correct position, and providing it with the neighbors field.
        wire = Wire(Neighbors(*boolNeighbors), (
            (position[0] * 100) + GRID_POSITION[0],
            (position[1] * 100) + GRID_POSITION[1]
        ))
        #add the wire instance to the grid
        self.grid[position] = wire

    def remove_wire(self, position: tuple[int, int]):
        """
        Removes a wire from a requested position
        """

        #do nothing if requested position does not hold a wire.
        if not isinstance(self.grid[position], Wire): return

        #remove wire
        self.grid[position] = None
        
        #update the wire's neighbors
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
        """
        Ticks the grid's simulation once
        """
        #if no more inputs, skip tick
        if self.get(0, 2).value_index == len(self.get(0, 2).values) - 1:
            return

        #tick all ioports
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
                        neighbor_instance.update_surf()
                elif isinstance(neighbor_instance, MicroPointer):
                    if neighbor_instance.portId != None:
                        if "in" in neighbor_instance.portId:
                            micro = self.get(*neighbor_instance.pointTo)
                            micro.__dict__[neighbor_instance.portId] = c_val

                visited.append(neighbor)

    def reset_sim(self):
        """
        Resets the simulation to it's default state.
        """
        for item in self.grid.values():
            if isinstance(item, Microcontroller):
                item.current_sim_line = 0
                item.in1 = 0
                item.in2 = 0
                item.ou1 = 0
                item.ou2 = 0
                item.mhs = 0
                item.ics = 0
                item.update_surf()
            elif isinstance(item, Wire):
                item.value = 0
                item.update_surf()
            elif isinstance(item, IOPort):
                item.value_index = 0
                item.output_value = 0
                item.first_tick = True
                item.update_surf()