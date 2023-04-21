#import modules
import pygame
import typing
from math import floor
from collections import deque
from Classes.Game.Microcontroller import Microcontroller, MicroPointer
from Classes.Game.Wire import Wire, Neighbors
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
        self.grid[(0, 2)] = IOPort("Input 1", (20, 220), input1values)

        self.grid[(0, 4)] = IOPort("Input 2", (20, 420), input2values)

        self.grid[(14, 2)] = IOPort("Output 1", (1420, 220))

        self.grid[(14, 4)] = IOPort("Output 2", (1420, 420))

        #set up some variables to allow creating wires
        self.mouse_dragging = False
        self.last_mouse_pos = None
    
    def update(self):
        """
        Updates the grid, handling things like user input, and sprite updates.
        """

        #get all events
        events = pygame.event.get()
        
        #check the mouse is in the bounds of the grid
        mouse_position = pygame.mouse.get_pos()
        mb1_pressed, _, mb2pressed = pygame.mouse.get_pressed()
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

        if self.mouse_dragging:
            if mb1_pressed:
                self.add_wire(self.last_mouse_pos, mouse_grid)
                self.last_mouse_pos = mouse_grid
            else:
                self.mouse_dragging = False
                self.last_mouse_pos = None
        else:
            if mb1_pressed:
                self.mouse_dragging = True
                self.last_mouse_pos = mouse_grid

        if mb2pressed:
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

        #make sure micro wont overlap wires, IOPorts or another micro
        for item in [self.get(*center_position, mod) for mod in [
            (0, 0),
            (-1, 0),
            (-1, 1),
            (1, 0),
            (1, 1),
            (0, 1)
        ]]:
            if isinstance(item, (Wire, IOPort, Microcontroller, MicroPointer)): return

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
            x = center_position[0] + modifier[0]
            y = center_position[1] + modifier[1]
            self.grid[(x, y)] = MicroPointer(center_position, modifier[2])
            self.grid[(x, y)].rect.topleft = (
                x * 100 + GRID_POSITION[0],
                y * 100 + GRID_POSITION[1]
            )
            
            
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
        for modifier, isPort in [
            ((0, 0), False),
            ((-1, 0), True),
            ((-1, 1), True),
            ((1, 0), True),
            ((1, 1), True),
            ((0, 1), False)
        ]:
            pos = (microcontroller_pos[0] + modifier[0], microcontroller_pos[1] + modifier[1])
            self.grid[pos] = None
            if isPort:
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
                    gotten = self.get(*pos, modifier)
                    if isinstance(gotten, Wire):
                        wire_connections = gotten.connections
                        wire_connections.__dict__[direction] = False
                        gotten.update_connections(wire_connections)


    def add_wire(self, position1: tuple[int, int], position2: tuple[int, int]):
        """
        Creates a wire connecting two provided grid spaces
        """
        MODIFIER_TO_STRING = {
            (0, -1): "down",
            (0, 1): "up",
            (-1, 0): 'right',
            (1, 0): "left"
        }

        instance1 = self.get(*position1)
        instance2 = self.get(*position2)

        #make sure it isn't asking to write on top of a micro
        if isinstance(instance1, Microcontroller) or isinstance(instance2, Microcontroller): return

        #make sure it isn't asking to add a wire spanning more than 2 grid cells
        if abs(position1[0] - position2[0]) > 1 or abs(position1[1] - position2[1]) > 1: return

        #make sure it isn't asking to add a diagonal wire
        if abs(position1[0] - position2[0]) > 0 and abs(position1[1] - position2[1]) > 0: return

        if isinstance(instance1, (Wire, type(None))) and isinstance(instance2, (Wire, type(None))):
            if position1==position2:
                if instance1 == None:
                    self.grid[position1] = Wire(
                        Neighbors(*([False]*4)),
                        (
                            (position1[0] * 100) + GRID_POSITION[0],
                            (position1[1] * 100) + GRID_POSITION[1]
                        )
                    )
            else:
                for main, maininstance, neighbor in [(position1, instance1, position2), (position2, instance2, position1)]:
                    if isinstance(maininstance, Wire):
                        wire = maininstance
                        wire_connections = wire.connections
                        wire_connections.__dict__[
                            MODIFIER_TO_STRING[
                                (
                                    main[0] - neighbor[0],
                                    main[1] - neighbor[1]
                                )
                            ]
                        ] = True
                        wire.update_connections(wire_connections)
                    else:
                        wire_connections = Neighbors(False, False, False, False)
                        wire_connections.__dict__[
                            MODIFIER_TO_STRING[
                                (
                                    main[0] - neighbor[0],
                                    main[1] - neighbor[1]
                                )
                            ]
                        ] = True
                        self.grid[main] = Wire(
                            wire_connections,
                            (
                                (main[0] * 100) + GRID_POSITION[0],
                                (main[1] * 100) + GRID_POSITION[1]
                            )
                        )
        elif (
            (isinstance(instance1, (Wire, type(None))) and (isinstance(instance2, (IOPort, MicroPointer)))) or
            (isinstance(instance2, (Wire, type(None))) and (isinstance(instance1, (IOPort, MicroPointer))))
        ):
            
            (
                wire_position, 
                other_position,
                wire_instance,
                other_instance
            ) = (
                (position1, position2, instance1, instance2)
                if isinstance(instance1, (Wire, type(None))) 
                else (position2, position1, instance2, instance1)
            )

            wire = wire_instance if isinstance(wire_instance, Wire) else Wire(Neighbors(*([False] * 4)), (
                (wire_position[0] * 100) + GRID_POSITION[0],
                (wire_position[1] * 100) + GRID_POSITION[1]
            ))
            if wire_instance == None: self.grid[wire_position] = wire

            connections = wire.connections
            flag = True

            direction = MODIFIER_TO_STRING[(
                wire_position[0] - other_position[0],
                wire_position[1] - other_position[1]
            )]
            if isinstance(other_instance, MicroPointer):
                flag = (direction != "up" and direction != "down")
                other_instance.set_connected(flag)


            if isinstance(other_instance, IOPort):
                other_connections = other_instance.subwire.connections
                other_connections.__dict__[MODIFIER_TO_STRING[(
                    other_position[0] - wire_position[0],
                    other_position[1] - wire_position[1]
                )]] = True
                other_instance.subwire.update_connections(other_connections)
                other_instance.update_surf()
            
            connections.__dict__[direction] = flag
            
            wire.update_connections(connections)
            

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
            gotten = self.get(*position, modifier)
            if isinstance(gotten, Wire):
                wire_connections = gotten.connections
                wire_connections.__dict__[direction] = False
                gotten.update_connections(wire_connections)
            elif isinstance(gotten, IOPort):
                wire_connections = gotten.subwire.connections
                wire_connections.__dict__[direction] = False
                gotten.subwire.update_connections(wire_connections)
                gotten.update_surf()
            elif isinstance(gotten, MicroPointer):
                gotten.set_connected(False)

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
                for mod in (current_instance if isinstance(current_instance, Wire) else current_instance.subwire).connections.to_modifiers()
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
                        neighbor_instance.update_surf()
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


            neighbors = None
            if isinstance(current_instance, Wire):
                neighbors = [
                    pos
                    for mod in current_instance.connections.to_modifiers()
                    if self.get(*(pos := (current[0] + mod[0], current[1] + mod[1]))) != None
                    and pos not in visited
                ]
            else:
                mod = current_instance.to_modifier()
                neighbors = [
                    (current[0] + mod[0], current[1] + mod[1])
                ] if current_instance.connected else []

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