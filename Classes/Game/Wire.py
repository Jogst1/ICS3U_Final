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

class WireNeighbors():
    def __init__(self, up: bool, down: bool, left: bool, right: bool):
        self.up = up
        self.down = down
        self.left = left
        self.right = right

class Wire(pygame.sprite.Sprite):
    def __init__(self, neighbors: WireNeighbors, position: tuple[int]):
        super().__init__()
        
        self.value = 0
        self.position = position
        self.current_neighbors = neighbors
        self.update_neighbors(neighbors)

        
    def update_surf(self):
        self.surf = self.clean_surf.copy()
        render = FONT.render(str(self.value), True, (0, 0, 0))
        rect = render.get_rect()
        rect.center = (50, 50)
        self.surf.blit(render, rect)

    def update_neighbors(self, neighbors: WireNeighbors):
        self.current_neighbors = neighbors
        num_neighbors = len([x for x in [neighbors.up, neighbors.down, neighbors.left, neighbors.right] if x])
        if num_neighbors == 0:
            self.clean_surf = IMAGES["0"]
        elif num_neighbors == 1:
            self.clean_surf = IMAGES["1"]
            angle = 0
            if neighbors.up:
                angle = 90   
            elif neighbors.left:
                angle = 180
            elif neighbors.down:
                angle = 270
            self.clean_surf = pygame.transform.rotate(self.clean_surf, angle)

        elif num_neighbors == 3:
            self.clean_surf = IMAGES["3"]

            if neighbors.left:
                if neighbors.right and neighbors.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 90)           
                elif neighbors.down and neighbors.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 180)
                elif neighbors.down and neighbors.right:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 270)
                    
        elif num_neighbors == 4:
            self.clean_surf = IMAGES["4"]
        else: #2
            if (neighbors.up and neighbors.down) or (neighbors.left and neighbors.right):
                self.clean_surf = IMAGES["2-straight"]
                if neighbors.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 90)
            else:
                self.clean_surf = IMAGES["2-bent"]
                if neighbors.left:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 270 if neighbors.down else 180)
                elif neighbors.up:
                    self.clean_surf = pygame.transform.rotate(self.clean_surf, 90)
        
        self.rect = self.clean_surf.get_rect()
        self.rect.topleft = self.position
        self.update_surf()


