import pygame
from Classes.Instance import Instance
from Util.Assets import Assets

#set up font constant for rendering text labels
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
    
class Wire(Instance):
    def __init__(self, parent: Instance, connections: Neighbors, position: tuple[int, int], zOffset: int = 0):
        super().__init__(parent)

        self.position = position
        self.zoffset = zOffset

        self.update_connections(connections)
        self.update_value(0)

    def update_value(self, value: int):
        self.value = value
        render = FONT.render(str(self.value), True, (0, 0, 0))
        rect = render.get_rect(
            center=(50+self.position[0], 50+self.position[1])
        )
        self.renderables["text"] = (
            (render,
            rect),
            1 + self.zoffset
        )

    def update_connections(self, connections:Neighbors):
        self.connections = connections
        num_connections = len([x for x in [connections.up, connections.down, connections.left, connections.right] if x])
        
        surf = None

        if num_connections == 0:
            surf = Assets.Game.Wires["0"].png
        elif num_connections == 1:
            surf = Assets.Game.Wires["1"].png
            angle = 0
            if connections.up:
                angle = 90   
            elif connections.left:
                angle = 180
            elif connections.down:
                angle = 270
            surf = pygame.transform.rotate(surf, angle)

        elif num_connections == 3:
            surf = Assets.Game.Wires["3"].png

            if connections.left:
                if connections.right and connections.up:
                    surf = pygame.transform.rotate(surf, 90)           
                elif connections.down and connections.up:
                    surf = pygame.transform.rotate(surf, 180)
                elif connections.down and connections.right:
                    surf = pygame.transform.rotate(surf, 270)
                    
        elif num_connections == 4:
            surf = Assets.Game.Wires["4"].png
        else: #2
            if (connections.up and connections.down) or (connections.left and connections.right):
                surf = Assets.Game.Wires["2-straight"].png
                if connections.up:
                    surf = pygame.transform.rotate(surf, 90)
            else:
                surf = Assets.Game.Wires["2-bent"].png
                if connections.left:
                    surf = pygame.transform.rotate(surf, 270 if connections.down else 180)
                elif connections.up:
                    surf = pygame.transform.rotate(surf, 90)

        rect = surf.get_rect(
            topleft = self.position
        )
        self.renderables["wire"] = (
            (
                surf, 
                rect
            ),
            2 + self.zoffset
        )