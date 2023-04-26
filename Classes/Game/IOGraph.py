import pygame
import math

IMAGE = pygame.image.load("Assets/Game/io_graph.png").convert_alpha(pygame.display.get_surface())
FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 12)

RED_COLOR = (163, 49, 35)
GREEN_COLOR = (0, 149, 61)

class IOGraph(pygame.sprite.Sprite):
    def __init__(self, input1: list[int], input2: list[int], expected1: list[int], expected2: list[int]):
        super().__init__()

        self.surf = IMAGE.copy()
        self.rect = self.surf.get_rect()
        self.actual1 = []
        self.actual2 = []
        
        self.LENGTH = len(input1)
        self.SPACING = math.ceil(748/self.LENGTH)
        self.MAX_LINE_HEIGHT = 125 - FONT.size("a")[1] - 3
        
        self.max_values = []

        for i, ls in enumerate([input1, input2, expected1, expected2]):
            max_value = max(ls)
            if i > 1: self.max_values.append(max_value)
            if max_value == 0: max_value = 1
            value_to_height = lambda x: (155 if not bool(i%2) else 278) - math.floor(self.MAX_LINE_HEIGHT * (x/max_value))
            
            prev_y = value_to_height(ls[0])+2

            for num, item in enumerate(ls):
                height = value_to_height(item)
                start_x = num * self.SPACING + 2 + (750 * int(i>1))
                pygame.draw.line(
                    self.surf,
                    RED_COLOR, 
                    (start_x, height),
                    ((num+1) * self.SPACING + (int(num != self.LENGTH-1)*2-1) + (750 * int(i>1)), height),
                    4
                )
                if num != 0:
                    pygame.draw.line(
                        self.surf,
                        RED_COLOR,
                        (start_x, prev_y),
                        (start_x, height-1),
                        4
                    )
                    prev_y = value_to_height(item)+2

                text_render = FONT.render(str(item), True, RED_COLOR)
                text_rect = text_render.get_rect()
                text_rect.midbottom = (start_x + round(self.SPACING * 0.5), height)
                self.surf.blit(text_render, text_rect)

        self.CLEAN_SURF = self.surf.copy()

    def add_actual(self, actual1_value: int, actual2_value: int):
        self.actual1.append(actual1_value)
        self.actual2.append(actual2_value)

        for i, ls in enumerate([self.actual1, self.actual2]):
            max_value = self.max_values[i]
            if max_value == 0: max_value = 1
            value_to_height = lambda x: (155 if i==0 else 278) - math.floor(self.MAX_LINE_HEIGHT * (x/max_value))
            
            prev_y = value_to_height(ls[-2] if len(ls)>1 else ls[-1])

            item = ls[-1]
            num = len(ls)-1

            height = value_to_height(item)
            start_x = num * self.SPACING + 2 + 750
            pygame.draw.line(
                self.surf,
                GREEN_COLOR, 
                (start_x, height),
                ((num+1) * self.SPACING + (int(num != self.LENGTH-1)*2-1) + 750, height),
                2
            )
            if num != 0:
                pygame.draw.line(
                    self.surf,
                    GREEN_COLOR,
                    (start_x, prev_y + int(prev_y != height)),
                    (start_x, height),
                    2
                )
                prev_y = value_to_height(item)

            text_render = FONT.render(str(item), True, GREEN_COLOR)
            text_rect = text_render.get_rect()
            text_rect.midbottom = (start_x + round(self.SPACING * 0.5), height)
            self.surf.blit(text_render, text_rect)
    

    def reset(self):
        self.actual1 = []
        self.actual2 = []
        self.surf = self.CLEAN_SURF.copy()