#throughout this file I use the __dict__ property, which i learned about from here:
#https://docs.python.org/3/reference/datamodel.html

import pygame
import typing
from collections import deque
from Classes.Instance import Instance, MouseState

from Classes.Game.Microcontroller import Microcontroller, MicroPointer, UpdateId
from Classes.Game.Wire import Wire, Neighbors
from Classes.Game.IOPort import IOPort

#set up some constants for use later
GRID_SIZE = (15, 7)
PLACE_MICROCONTROLLER_KEY = pygame.K_e
REMOVE_MICROCONTROLLER_KEY = pygame.K_q
GRID_SIZE_PIXELS = (1500, 700)
GRID_POSITION = (20, 20)
MICROCONTROLLER_OFFSET = 10

#set up some functions for more concise code later on
def is_wire_or_none(i):
    return isinstance(i, (Wire, type(None)))
def is_microp(i):
    return isinstance(i, MicroPointer)
def is_ioport(i):
    return isinstance(i, IOPort)

class Grid(Instance):
    def __init__(self, parent: Instance):
        super().__init__(parent)

        self.add_child((0, 2), IOPort(self, "Input 1", (20, 220), self.parent.puzzle.example_testcase.inputs))
        self.add_child((0, 4), IOPort(self, "Input 2", (20, 420), self.parent.puzzle.example_testcase.inputs2))
        self.add_child((14, 2), IOPort(self, "Output 1", (1420, 220)))
        self.add_child((14, 4), IOPort(self, "Output 2", (1420, 420)))

        self.mouse_dragging = False
        self.last_mouse_pos = None

    def update(self, events: list[pygame.event.Event], mouseState: MouseState, _: float):
        #if mouse is out of bounds of grid, return early and do nothing
        if (
            mouseState.x < GRID_POSITION[0] or
            mouseState.x > GRID_POSITION[0] + GRID_SIZE_PIXELS[0] or
            mouseState.y < GRID_POSITION[1] or
            mouseState.y > GRID_POSITION[1] + GRID_SIZE_PIXELS[1]
        ):
            return
        
        mouse_grid = (
            (mouseState.x - GRID_POSITION[0]) // 100,
            (mouseState.y - GRID_POSITION[1]) // 100
        )

        #handle placement and removal of microcontrollers
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == PLACE_MICROCONTROLLER_KEY:
                    self.add_microcontroller(mouse_grid)
                elif event.key == REMOVE_MICROCONTROLLER_KEY:
                    self.remove_microcontroller(mouse_grid)

        if self.mouse_dragging:
            if mouseState.lmb:
                self.add_wire(self.last_mouse_pos, mouse_grid)
                self.last_mouse_pos = mouse_grid
            else:
                self.mouse_dragging = False
                self.last_mouse_pos = None
        else:
            if mouseState.lmb:
                self.mouse_dragging = True
                self.last_mouse_pos = mouse_grid

        if mouseState.rmb:
            self.remove_wire(mouse_grid)

    def get(self, x: int, y: int, change: tuple[int, int] = (0, 0)) -> typing.Union[Microcontroller, MicroPointer, Wire, IOPort, None]:
        """
        Returns the item at a given grid space. Returns none if no item is present
        Supports an optional change tuple to modify the initial x,y
        """

        x += change[0]
        y += change[1]

        if (x, y) not in self.children:
            return None
        else:
            return self.children[(x, y)]
        
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
        self.add_child(
            center_position,
            Microcontroller(
                self,
                (
                    ((center_position[0] - 1) * 100) + GRID_POSITION[0] + MICROCONTROLLER_OFFSET,
                    (center_position[1] * 100) + GRID_POSITION[1] + MICROCONTROLLER_OFFSET
                )
            )
        )

        #create MicroPointer instances surrounding the micro
        for modifier in [
            (-1, 0, "in1"),
            (+1, 0, "ou2"),
            (-1, +1, "ou1"),
            (0, +1, None),
            (+1, +1, "in2")
        ]:
            x = center_position[0] + modifier[0]
            y = center_position[1] + modifier[1]
            self.add_child(
                (x, y),
                MicroPointer(self, center_position, modifier[2], (
                    x * 100 + GRID_POSITION[0],
                    y * 100 + GRID_POSITION[1]
                ))
            )

        #play the sfx
        pygame.mixer.Sound("Assets/Sounds/micro_place.mp3").play()

    def remove_microcontroller(self, position: tuple[int, int]):
        """
        Removes a microcontroller from a requested position
        """
        #check that the requested remove location is actually a microcontroller
        if not isinstance(self.get(*position), (Microcontroller, MicroPointer)): return

        microcontroller_pos = position if isinstance(self.get(*position), Microcontroller) else self.get(*position).pointTo

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
            self.remove_child(pos)
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

        #play the sfx
        pygame.mixer.Sound("Assets/Sounds/micro_delete.mp3").play()

    def add_wire(self, position1: tuple[int, int], position2: tuple[int, int]):
        """
        Creates a wire linking two provided grid spaces
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

        #if positions want to add wire between microcontroller (pointer) and wire:
        if (
            (is_wire_or_none(instance1) and is_microp(instance2)) or
            (is_microp(instance1) and is_wire_or_none(instance2))
        ):
            
            #set instance1 to the wire and instance2 to the micro
            (
                position1, 
                position2,
                instance1,
                instance2
            ) = (
                (position1, position2, instance1, instance2)
                if is_wire_or_none(instance1)
                else (position2, position1, instance2, instance1)
            )

            if position1[0] - position2[0] == 0 and position1[1] - position2[1] == 0: return

            direction = MODIFIER_TO_STRING[(
                position1[0] - position2[0],
                position1[1] - position2[1]
            )]
            if direction == "up" or direction == "down": return

            #set up a wire instance if instance1 happens to be none
            wire = instance1 if instance1 != None else Wire(
                self,
                Neighbors(*([False] * 4)),
                (
                    (position1[0] * 100) + GRID_POSITION[0],
                    (position1[1] * 100) + GRID_POSITION[1]
                )
            )
            if instance1 == None: self.add_child(position1, wire)

            #set up micropointer connected
            flag = (direction != "up" and direction != "down")
            instance2.set_connected(flag)

            #correctly configure wire connections
            connections = wire.connections
            connections.__dict__[direction] = flag
            wire.update_connections(connections)

            #play sfx if a connection was established
            if flag:
                pygame.mixer.Sound("Assets/Sounds/wire_place.mp3").play()
            
        elif (
            (is_wire_or_none(instance1) and is_ioport(instance2)) or
            (is_ioport(instance1) and is_wire_or_none(instance2))
        ):
            #set instance1 to the wire and instance2 to the ioport
            (
                position1, 
                position2,
                instance1,
                instance2
            ) = (
                (position1, position2, instance1, instance2)
                if is_wire_or_none(instance1)
                else (position2, position1, instance2, instance1)
            )

            #set up a wire instance if instance1 happens to be none
            wire = instance1 if instance1 != None else Wire(
                self,
                Neighbors(*([False] * 4)),
                (
                    (position1[0] * 100) + GRID_POSITION[0],
                    (position1[1] * 100) + GRID_POSITION[1]
                )
            )
            if instance1 == None: self.add_child(position1, wire)

            #update IOport subwire
            ioport_connections = instance2.children["subwire"].connections
            ioport_direction = MODIFIER_TO_STRING[(
                position2[0] - position1[0],
                position2[1] - position1[1]
            )]
            ioport_connections.__dict__[ioport_direction] = True
            instance2.children["subwire"].update_connections(ioport_connections)

            #update wire
            wire_connections = wire.connections
            wire_direction = MODIFIER_TO_STRING[(
                position1[0] - position2[0],
                position1[1] - position2[1]
            )]
            wire_connections.__dict__[wire_direction] = True
            wire.update_connections(wire_connections)

            #play sfx 
            pygame.mixer.Sound("Assets/Sounds/wire_place.mp3").play()

        #if both are wires
        elif is_wire_or_none(instance1) and is_wire_or_none(instance2):
            #if asking to just place 1 wire
            if position1 == position2:
                #make sure there's nothing there already
                if instance1 != None: return
                #add wire
                self.add_child(
                    position1,
                    Wire(
                        self,
                        Neighbors(*([False]*4)),
                        (
                            (position1[0] * 100) + GRID_POSITION[0],
                            (position1[1] * 100) + GRID_POSITION[1]
                        )
                    )
                )
                #play sfx
                pygame.mixer.Sound("Assets/Sounds/wire_place.mp3").play()

            #if asking to place 2 wires
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
                        self.add_child(main, Wire(
                            self,
                            wire_connections,
                            (
                                (main[0] * 100) + GRID_POSITION[0],
                                (main[1] * 100) + GRID_POSITION[1]
                            )
                        ))
                #play sfx
                pygame.mixer.Sound("Assets/Sounds/wire_place.mp3").play()
                    
    def remove_wire(self, position: tuple[int, int]):
        """
        Removes a wire from a requested position
        """
        #do nothing if requested position does not hold a wire.
        if not isinstance(self.get(*position), Wire): return

        #remove wire
        self.remove_child(position)
        
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
                wire_connections = gotten.children["subwire"].connections
                wire_connections.__dict__[direction] = False
                gotten.children["subwire"].update_connections(wire_connections)
            elif isinstance(gotten, MicroPointer):
                gotten.set_connected(False)

        #play the sfx
        pygame.mixer.Sound("Assets/Sounds/wire_delete.mp3").play()

    def tick(self):
        """
        Ticks the grid's simulation once
        """

        #if no more inputs, skip tick
        if self.get(0, 2).value_index == len(self.get(0, 2).values) - 1:
            return
        
        #tick all ioports
        for ioportpos in [(0, 2), (0, 4), (14, 2), (14, 4)]:
            ioport = self.get(*ioportpos)
            ioport.tick()
            ioport.update_visuals()

        #perform an initial breadth-first traversal of the wire networks starting from input nodes, ending at microcontroller ports
        visited = [(0, 2), (0, 4)]
        queue = deque(visited.copy())

        while len(queue) > 0:
            current = queue.pop()
            current_instance = self.get(*current)
            current_value = (
                current_instance.value 
                if isinstance(current_instance, Wire) else 
                current_instance.values[current_instance.value_index]
            )

            neighbors = [
                position
                for modifier in (
                    current_instance 
                    if isinstance(current_instance, Wire) else 
                    current_instance.children["subwire"]
                ).connections.to_modifiers()
                if self.get(*(position := (
                    current[0] + modifier[0], 
                    current[1] + modifier[1]
                ))) != None
                and position not in visited
            ]

            for neighbor in neighbors:
                neighbor_instance = self.get(*neighbor)

                if isinstance(neighbor_instance, Wire):
                    neighbor_instance.update_value(current_value)
                    queue.appendleft(neighbor)
                elif is_ioport(neighbor_instance):
                    if neighbor_instance.is_output_port():
                        neighbor_instance.output_value = current_value
                        neighbor_instance.update_visuals()
                elif is_microp(neighbor_instance):
                    if neighbor_instance.portId != None and "in" in neighbor_instance.portId:
                        micro = self.get(*neighbor_instance.pointTo)
                        micro.__dict__[neighbor_instance.portId] = current_value

                visited.append(neighbor)
        
        #do a simulation tick on all microcontrollers
        for micro in filter(lambda value: isinstance(value, Microcontroller), self.children.values()):
            micro.tick()
        
        #get a list of all the output ports for every microcontroller
            #i took the code for how to "flatten" a list of sublists from:
            # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists 
        visited = [
            item for sublist in 
            [
                [
                    (
                        micro_position[0]-1, 
                        micro_position[1]+1
                    ), 
                    (
                        micro_position[0]+1,
                        micro_position[1]
                    )
                ] 
                for micro_position in 
                filter(
                    lambda value: isinstance(self.get(*value), Microcontroller),
                    self.children.keys()
                )
            ] 
            for item in sublist
        ]
        queue = deque(visited.copy())

        #do another bfs to propagate output values from the microcontroller simulation tick
        while len(queue) > 0:
            current = queue.pop()
            current_instance = self.get(*current)
            current_value = (
                current_instance.value 
                if isinstance(current_instance, Wire) 
                else self.get(*current_instance.pointTo).__dict__[current_instance.portId]
            )

            neighbors = None
            if isinstance(current_instance, Wire):
                neighbors = [
                    position
                    for modifier in current_instance.connections.to_modifiers()
                    if self.get(*(position := (
                        current[0] + modifier[0],
                        current[1] + modifier[1]
                    ))) != None
                    and position not in visited
                ]
            else:
                modifier = current_instance.to_modifier()
                neighbors = [
                    (current[0] + modifier[0], current[1] + modifier[1])
                ] if current_instance.connected else []

            #if the current instance is a micropointer, prevent it from adding other micropointers to the neighbor list 
            if is_microp(current_instance):
                neighbors = [neighbor for neighbor in neighbors if not is_microp(self.get(*neighbor))]

            for neighbor in neighbors:
                neighbor_instance = self.get(*neighbor)

                if isinstance(neighbor_instance, Wire):
                    neighbor_instance.update_value(current_value)
                    queue.appendleft(neighbor)
                elif is_ioport(neighbor_instance):
                    if neighbor_instance.is_output_port():
                        neighbor_instance.output_value = current_value
                        neighbor_instance.update_visuals()
                elif is_microp(neighbor_instance):
                    if neighbor_instance.portId != None and "in" in neighbor_instance.portId:
                        micro = self.get(*neighbor_instance.pointTo)
                        micro.__dict__[neighbor_instance.portId] = current_value

                visited.append(neighbor)
    
    def reset(self):
        """
        Resets the simulation to it's default state.
        """

        for item in self.children.values():
            if isinstance(item, Microcontroller):
                item.current_sim_line = 0
                item.in1 = 0
                item.in2 = 0
                item.ou1 = 0
                item.ou2 = 0
                item.mhs = 0
                item.ics = 0
                item.update_visuals(UpdateId.Mhs)
                item.update_visuals(UpdateId.Ics)
            elif isinstance(item, Wire):
                item.update_value(0)
            elif isinstance(item, IOPort):
                item.value_index = 0
                item.output_value = 0
                item.first_tick = True
                item.update_visuals()