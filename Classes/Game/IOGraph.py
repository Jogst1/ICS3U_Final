import pygame
import math
from Classes.Instance import Instance
from Util.Assets import Assets


FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 12)
RED_COLOR = (163, 49, 35)
GREEN_COLOR = (0, 149, 61)

def line_fn_generator(color, pos1, pos2, width):
    def line(screen):
        pygame.draw.line(screen, color, pos1, pos2, width)
    return line

class IOGraph(Instance):
    def __init__(self, parent: Instance):
        super().__init__(parent)

        example_testcase = self.parent.puzzle.example_testcase
        input1 = example_testcase.inputs
        input2 = example_testcase.inputs2
        expected1 = example_testcase.expected_outputs
        expected2 = example_testcase.expected_outputs2


        self.actual1 = []
        self.actual2 = []
        
        self.LENGTH = len(input1)
        self.SPACING = math.ceil(748/self.LENGTH)
        self.MAX_LINE_HEIGHT = 125 - FONT.size("a")[1] - 3
        
        self.max_values = []

        self.static_lines = []
        self.dyn_lines = []

        self.renderables["background"] = (
            (
                Assets.Game.io_graph.png,
                Assets.Game.io_graph.png.get_rect(
                    topleft = (20, 750)
                )
            ),
            2
        )

        def render_lines(screen: pygame.surface.Surface):
            for line_fn in self.static_lines:
                line_fn(screen)
            for line_fn in self.dyn_lines:
                line_fn(screen)

        self.renderables["lines"] = (
            render_lines,
            1
        )

        for i, ls in enumerate([input1, input2, expected1, expected2]):
            max_value = max(ls)
            if i > 1: self.max_values.append(max_value)
            if max_value == 0: max_value = 1
            value_to_height = lambda x: (155 if not bool(i%2) else 278) - math.floor(self.MAX_LINE_HEIGHT * (x/max_value))
            
            prev_y = value_to_height(ls[0])+2

            for num, item in enumerate(ls):
                height = value_to_height(item)
                start_x = num * self.SPACING + 2 + (750 * int(i>1))
                self.static_lines.append(line_fn_generator(
                    RED_COLOR, 
                    (start_x + 20, height+ 750),
                    ((num+1) * self.SPACING + (int(num != self.LENGTH-1)*2-1) + (750 * int(i>1)) + 20, height + 750),
                    4
                ))
                if num != 0:
                    if prev_y > height:                            
                        self.static_lines.append(line_fn_generator(
                            RED_COLOR,
                            (start_x + 20, prev_y+750),
                            (start_x + 20, height-1+750),
                            4
                        ))
                    else:
                        self.static_lines.append(line_fn_generator(
                            RED_COLOR,
                            (start_x+20, prev_y-3+750),
                            (start_x+20, height+1+750),
                            4
                        ))
                    prev_y = value_to_height(item)+2

                text_render = FONT.render(str(item), True, RED_COLOR)
                text_rect = text_render.get_rect()
                text_rect.midbottom = (start_x+20 + round(self.SPACING * 0.5), height+750)
                self.renderables[f"static_text_{text_render.__hash__()}"] = (
                    (
                        text_render,
                        text_rect
                    ),
                    1
                )


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
            self.dyn_lines.append(line_fn_generator(
                GREEN_COLOR,
                (start_x + 20, height + 750),
                (
                    (num+1) * self.SPACING + (int(num != self.LENGTH-1)*2-1) + 770, 
                    height + 750
                ),
                2
            ))
            if num != 0:
                self.dyn_lines.append(line_fn_generator(
                    GREEN_COLOR,
                    (start_x+20, prev_y + int(prev_y != height)+750),
                    (start_x+20, height+750),
                    2
                ))
                prev_y = value_to_height(item)

            text_render = FONT.render(str(item), True, GREEN_COLOR)
            text_rect = text_render.get_rect()
            text_rect.midbottom = (start_x + round(self.SPACING * 0.5) + 20, height + 750)
            self.renderables[f"dyn_text_{text_render.__hash__()}"] = (
                (
                    text_render,
                    text_rect
                ),
                1
            )
        

    def reset(self):
        """
        Clears all dynamic lines in the IOGraph, resetting it to it's default state
        """
        self.actual1 = []
        self.actual2 = []

        self.dyn_lines = []

        for name in self.renderables.copy().keys():
            if "dyn_text_" in name:
                del self.renderables[name]