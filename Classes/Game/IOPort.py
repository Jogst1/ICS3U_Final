import pygame

IMAGE = pygame.image.load("Assets/Game/ioport.png").convert_alpha(pygame.display.get_surface())
FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 10)

class IOPort(pygame.sprite.Sprite):
    """
    Represents an IO port, which can be either input or output
    """
    def __init__(self, label: str, values: list[int]=[]):

        super().__init__()

        #for input
        self.value_index = 0
        self.values = values

        #for output
        self.output_value = 0

        self.label = label

        #set up a surface and rect for rendering. this surf here will be modified, and is kept as a constant to remain pristine.
        self.CONSTANT_SURF = IMAGE.copy()
        self.rect = self.CONSTANT_SURF.get_rect()

        #render the label text onto the surface
        text = FONT.render(label, True, (0, 0, 0))
        textrect = text.get_rect()
        textrect.midtop = (30, 15)
        self.CONSTANT_SURF.blit(text, textrect)

        #to keep track of if the ioport is on its first tick or not
        self.first_tick = True

        #update the surface with initial values
        self.update_surf()

    def is_output_port(self):
        """
        Returns whether the port is an output port (if the port label contains 'output')
        """
        return ("output" in self.label.lower())

    def update_surf(self):
        """
        Updates the IOPort's surface with the value it is currently on
        """

        self.surf = self.CONSTANT_SURF.copy()
        val = self.output_value if self.is_output_port() else self.values[self.value_index]
        text = FONT.render(str(val), True, (0, 0, 0))
        textrect = text.get_rect()
        textrect.midtop = (30, 15+18)
        self.surf.blit(text,textrect)
        

    def do_sim_tick(self):
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
    