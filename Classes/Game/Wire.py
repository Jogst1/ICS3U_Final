import pygame

surf_for_convert = pygame.display.get_surface()
IMAGES = {
    "1": pygame.image.load("Assets/Game/Wires/1.png").convert_alpha(surf_for_convert),
    "2-bent": pygame.image.load("Assets/Game/Wires/2-bent.png").convert_alpha(surf_for_convert),
    "2-straight": pygame.image.load("Assets/Game/Wires/2-straight.png").convert_alpha(surf_for_convert),
    "3": pygame.image.load("Assets/Game/Wires/3.png").convert_alpha(surf_for_convert),
    "4": pygame.image.load("Assets/Game/Wires/4.png").convert_alpha(surf_for_convert),
}

class WireNeighbors():
    def __init__(self, up: bool, down: bool, left: bool, right: bool):
        self.up = up
        self.down = down
        self.left = left
        self.right = right

class Wire(pygame.sprite.Sprite):
    def __init__(self, neighbors: WireNeighbors, position: tuple[int]):
        self.position = position
        self.current_neighbors = neighbors
        self.update_neighbors(neighbors)
        

    def update_neighbors(self, neighbors: WireNeighbors):
        self.current_neighbors = neighbors
        num_neighbors = len([x for x in [neighbors.up, neighbors.down, neighbors.left, neighbors.right] if x])
        if num_neighbors == 1 or num_neighbors == 0:
            self.surf = IMAGES["1"]
            angle = 0
            if neighbors.up:
                angle = 90   
            elif neighbors.left:
                angle = 180
            elif neighbors.down:
                angle = 270
            self.surf = pygame.transform.rotate(self.surf, angle)

        elif num_neighbors == 3:
            self.surf = IMAGES["3"]

            if neighbors.left:
                if neighbors.right and neighbors.up:
                    self.surf = pygame.transform.rotate(self.surf, 90)           
                elif neighbors.down and neighbors.up:
                    self.surf = pygame.transform.rotate(self.surf, 180)
                elif neighbors.down and neighbors.right:
                    self.surf = pygame.transform.rotate(self.surf, 270)
                    
        elif num_neighbors == 4:
            self.surf = IMAGES["4"]
        else: #2
            if (neighbors.up and neighbors.down) or (neighbors.left and neighbors.right):
                self.surf = IMAGES["2-straight"]
                if neighbors.up:
                    self.surf = pygame.transform.rotate(self.surf, 90)
            else:
                self.surf = IMAGES["2-bent"]
                if neighbors.left:
                    self.surf = pygame.transform.rotate(self.surf, 270 if neighbors.down else 180)
                elif neighbors.up:
                    self.surf = pygame.transform.rotate(self.surf, 90)
        
        self.rect = self.surf.get_rect()
        self.rect.topleft = self.position


