import pygame

surf_for_convert = pygame.display.get_surface()
IMAGES = {
    "0": pygame.image.load("Assets/Game/Wires/0.png").convert_alpha(surf_for_convert),
    "1": pygame.image.load("Assets/Game/Wires/1.png").convert_alpha(surf_for_convert),
    "2-bent": pygame.image.load("Assets/Game/Wires/2-bent.png").convert_alpha(surf_for_convert),
    "2-straight": pygame.image.load("Assets/Game/Wires/2-straight.png").convert_alpha(surf_for_convert),
    "3": pygame.image.load("Assets/Game/Wires/3.png").convert_alpha(surf_for_convert),
    "4": pygame.image.load("Assets/Game/Wires/4.png").convert_alpha(surf_for_convert),
}
FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 16)

class Neighbors():
    def __init__(self, up: bool, down: bool, left: bool, right: bool):
        self.up = up
        self.down = down
        self.left = left
        self.right = right

    def to_modifiers(self) -> list[tuple[int, int]]:
        return [ 
            modifier for flag, modifier 
            in zip(
                [self.up, self.down, self.left, self.right], 
                [
                    (0, -1),
                    (0, 1),
                    (-1, 0),
                    (1, 0)
                ]
            ) 
            if flag
        ]

class Wire(pygame.sprite.Sprite):
    def __init__(self, connections: Neighbors, position: tuple[int]):
        super().__init__()
        
        self.value = 0
        self.position = position
        self.connections = connections
        self.update_connections(connections)

        
    def update_surf(self):
        self.surf = self.clean_surf.copy()
        render = FONT.render(str(self.value), True, (0, 0, 0))
        rect = render.get_rect()
        rect.center = (50, 50)
        self.surf.blit(render, rect)

    def update_connections(self, connections: Neighbors):
        self.connections = connections
        num_connections = len([x for x in [connections.up, connections.down, connections.left, connections.right] if x])
        if num_connections == 0:
            self.clean_surf = IMAGES["0"]
        elif num_connections == 1:
            self.clean_surf = IMAGES["1"]
            angle = 0
            if connections.up:
                angle = 90   
            elif connections.left:
                angle = 180
            elif connections.down:
                angle = 270
            self.clean_surf = pygame.transform.rotate(self.clean_surf, angle)

        elif num_connections == 3:
            self.clean_surf = IMAGES["3"]

            if connections.left:
                if connections.right and connections.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 90)           
                elif connections.down and connections.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 180)
                elif connections.down and connections.right:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 270)
                    
        elif num_connections == 4:
            self.clean_surf = IMAGES["4"]
        else: #2
            if (connections.up and connections.down) or (connections.left and connections.right):
                self.clean_surf = IMAGES["2-straight"]
                if connections.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 90)
            else:
                self.clean_surf = IMAGES["2-bent"]
                if connections.left:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 270 if connections.down else 180)
                elif connections.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 90)
        
        self.rect = self.clean_surf.get_rect()
        self.rect.topleft = self.position
        self.update_surf()


