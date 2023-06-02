import pygame
import typing
from Classes.Instance import Instance
from Classes.Game.Wire import Neighbors, Wire
from Util.Assets import Assets

FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 10)

class IOPort(Instance):
    """
    Represents an IO port, which can be either input or output
    """

    def __init__(self, parent: Instance, label: str, position: tuple[int, int], values: list[int]=[]):
        super().__init__(parent)

        #for input
        self.value_index = 0
        self.values = values

        #for output
        self.output_value = 0

        self.label = label
        self.position = position

        #add sub-wire
        self.add_child(
            "subwire",
            Wire(
                self,
                Neighbors(*([False] * 4)),
                position,
                2
            ),
        )

        #render the label text
        textrender = FONT.render(label, True, (0, 0, 0))
        self.renderables["label"] = (
            (textrender,
            textrender.get_rect(
                midtop = (position[0] + 50, position[1] + 35)
            )),
            1
        )

        #render the icon
        self.renderables["icon"] = (
            (Assets.Game.ioport.png,
            Assets.Game.ioport.png.get_rect(topleft=position)),
            2
        )

        #to keep track of if the ioport is on its first tick or not
        self.first_tick = True

        self.update_visuals()

    def is_output_port(self) -> bool:
        """
        Returns whether the port is an output port (if the port label contains 'output')
        """
        return ("output" in self.label.lower())
    
    def update_visuals(self):
        """
        Updates the visuals for the ioport
        """

        value = self.output_value if self.is_output_port() else self.values[self.value_index]
        render = FONT.render(str(value), True, (0, 0, 0))
        self.renderables["value"] = (
            (
                render,
                render.get_rect(
                    midtop = (
                        50 + self.position[0],
                        50 + self.position[1]
                    )
                )
            ),
            1
        )
    
    def tick(self):
        """
        Performs a simulation tick, updating the input value if it is an input port, and doing nothing if it is an output port or it is the first tick
        """

        if self.first_tick: 
            self.first_tick = False
            return
        
        if self.is_output_port():
            pass
        else:
            self.value_index += 1
            self.value_index = min(self.value_index, len(self.values)-1)