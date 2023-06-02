from math import *
import typing
import pygame
from pygame import gfxdraw
from Classes.Instance import Instance, MouseState


class ImageButton(Instance):
    """
    An Image Button class, with an on-click event, and expand-on-hover behavior.
    """

    def __init__(
            self, 
            parent: Instance, 
            image: pygame.Surface, 
            onclick: typing.Callable, 
            position: tuple[int, int] = (0, 0),
            expand: float = None, 
            zIndex: int = 1
        ):
        super().__init__(parent)

        self.button_unexpanded = (
            (
                image,
                image.get_rect(
                    topleft=position
                )
            ),
            zIndex
        )
        self.button_expanded = (
            (
                pygame.transform.smoothscale_by(image, expand if expand != None else 1),
                image.get_rect(
                    topleft=position
                ).scale_by(expand if expand != None else 1, expand if expand != None else 1)
            ),
            zIndex
        )
        self.onclick = onclick
        self.expand = expand

        self.renderables["button"] = self.button_unexpanded

        self.expanded = False
        self.debounce = False

    def update(self, _: list[pygame.event.Event], mouseState: MouseState, __: float):

        #if mouse is hovering over button
        if self.renderables["button"][0][1].collidepoint(mouseState.x, mouseState.y):
            if mouseState.lmb and not self.debounce and ("cross" not in self.children):
                self.debounce = True
                #play sfx
                pygame.mixer.Sound("Assets/Sounds/button_onclick.mp3").play()
                #run the onclick function
                self.onclick()
            
            #if unexpanded
            if self.expand != None and not self.expanded:
                #expand
                self.renderables["button"] = self.button_expanded
                self.expanded = True

                #play the hover sfx
                s=pygame.mixer.Sound("Assets/Sounds/button_hover.mp3")
                s.set_volume(0.2)
                s.play()

        else:
            #if expanded
            if self.expanded:
                #unexpand
                self.renderables["button"] = self.button_unexpanded
                self.expanded = False

        if not mouseState.lmb:
            self.debounce = False

#taken from https://stackoverflow.com/questions/68522726/how-to-set-alpha-transparency-property-using-pygame-draw-line
def aaline(surface, color, start_pos, end_pos, width=1):
    """ Draws wide transparent anti-aliased lines. """
    # ref https://stackoverflow.com/a/30599392/355230

    x0, y0 = start_pos
    x1, y1 = end_pos
    midpnt_x, midpnt_y = (x0+x1)/2, (y0+y1)/2  # Center of line segment.
    length = hypot(x1-x0, y1-y0)
    angle = atan2(y0-y1, x0-x1)  # Slope of line.
    width2, length2 = width/2, length/2
    sin_ang, cos_ang = sin(angle), cos(angle)

    width2_sin_ang  = width2*sin_ang
    width2_cos_ang  = width2*cos_ang
    length2_sin_ang = length2*sin_ang
    length2_cos_ang = length2*cos_ang

    # Calculate box ends.
    ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang  + length2_sin_ang)
    ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang  - length2_sin_ang)
    bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang  + length2_sin_ang)
    br = (midpnt_x - length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang  - length2_sin_ang)

    pygame.gfxdraw.aapolygon(surface, (ul, ur, br, bl), color)
    pygame.gfxdraw.filled_polygon(surface, (ul, ur, br, bl), color)


class Cross(Instance):
    """
    Crosses out an imagebutton, indicating it cannot do anything
    """
    parent: ImageButton
    
    def __init__(self, parent: Instance):
        super().__init__(parent)

        def lines(screen):
            rect: pygame.Rect = self.parent.renderables["button"][0][1]
            aaline(
                screen,
                (163, 49, 35),
                rect.topleft,
                rect.bottomright,
                8
            )
            aaline(
                screen,
                (163, 49, 35),
                rect.topright,
                rect.bottomleft,
                8
            )
        self.renderables["lines"] = (
            lines,
            0
        )