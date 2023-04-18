import pygame

IMAGE = pygame.image.load("Assets/Game/ioport.png").convert_alpha(pygame.display.get_surface())
FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 10)

class IOPort(pygame.sprite.Sprite):
    def __init__(self, label, values=[]):
        super().__init__()

        self.value_index = 0
        self.values = values

        #for output
        self.output_value = 0

        self.label = label

        self.CONSTANT_SURF = IMAGE.copy()
        self.rect = self.CONSTANT_SURF.get_rect()

        text = FONT.render(label, True, (0, 0, 0))
        textrect = text.get_rect()
        textrect.midtop = (30, 15)

        self.CONSTANT_SURF.blit(text, textrect)

        self.first_tick = True

        self.update_surf()

    def is_output_port(self):
        return ("output" in self.label.lower())

    def update_surf(self):
        self.surf = self.CONSTANT_SURF.copy()
        val = self.output_value if self.is_output_port() else self.values[self.value_index]
        text = FONT.render(str(val), True, (0, 0, 0))
        textrect = text.get_rect()
        textrect.midtop = (30, 15+18)
        self.surf.blit(text,textrect)
        

    def do_sim_tick(self):
        if self.first_tick: 
            self.first_tick = False
            return
        
        if self.is_output_port():
            pass
        else:
            self.value_index += 1
            self.value_index = self.value_index % len(self.values)
    