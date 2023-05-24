import pygame
import math
import typing

class ImageButton(pygame.sprite.Sprite):
    """
    A general purpose class for images as buttons. Allows for onclick events, and an expand-on-hover feature.
    """
    def __init__(self, image: pygame.Surface, position: tuple, onclick: typing.Callable, expandOnHover:float=None):
        """
        Parameters
        ----------
        image:
            The image to display on the button
        position:
            The (x, y) position of where to display the button (uses top-left)
        onclick:
            The function to be called when the button is clicked
        expandOnHover:
            The factor by which the button will be scaled when hovered. Optional, omit to not scale at all.
        """
        super().__init__()
        self.surf = image
        #store the original image to switch back to after being scaled, since repeatedly scaling and de-scaling would leave artifacts
        self.ORIGINAL_SURF = image
        #position the button
        self.rect = self.surf.get_rect(
            topleft = (
                position[0],
                position[1]
            )
        )
        self.onclick = onclick
        self.expandOnHover = expandOnHover
        #calculate the difference in size when scaled, for both x and y
        if self.expandOnHover != None:
            self.expandXDiff = math.ceil(self.rect.size[0] * expandOnHover - self.rect.size[0])
            self.expandYDiff = math.ceil(self.rect.size[1] * expandOnHover - self.rect.size[1])
        #variables for keeping track of states/debouncing
        self.debounce = False
        self.expanded = False

    def update(self):
        """
        Updates the expand-on-hover behaviour and triggers onclick events for the button.
        """
        #get the state of the mouse, will be True if mouse1 is pressed, False if not
        mouse_state = pygame.mouse.get_pressed()[0]

        #check if the mouse is hovering on the button
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            #check if the mouse is clicking the button, and has not already clicked it very recently
            #(debounce mainly just prevents the button from being "held down", and makes it impossible to click again without first releasing the mouse)
            if mouse_state == True and self.debounce == False:
                #enable debounce
                self.debounce = True
                #play the onclick noise
                pygame.mixer.Sound("Assets/Sounds/button_onclick.mp3").play()

                #trigger the onclick event
                self.onclick()
            
            #check if the button should expand on hover, and is not already expanded
            if self.expandOnHover != None and self.expanded == False:

                #scale the button by the given expandOnHover factor
                self.surf = pygame.transform.smoothscale_by(self.surf, self.expandOnHover)
                #update the rect
                self.rect.scale_by_ip(self.expandOnHover)
                #enable the expanded flag
                self.expanded = True
                #play the hover sfx
                s=pygame.mixer.Sound("Assets/Sounds/button_hover.mp3")
                s.set_volume(0.2)
                s.play()
        else:
            #if the mouse isn't hovering, and the button is expanded,
            if self.expanded == True:
                #unexpand the button
                self.surf = self.ORIGINAL_SURF
                #update the rect
                self.rect.scale_by_ip(2 - self.expandOnHover)
                #disable the expanded flag
                self.expanded = False

        
        #disable the debounce flag once the mouse is released
        if mouse_state == False:
            self.debounce = False

        