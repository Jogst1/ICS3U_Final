from __future__ import annotations
import pygame
import typing

instanceCache: set[Instance] = set()

"""
Define a new type to hold any renderable. A renderable can be one of these three:
A tuple of (Surface, Rect)
A Surface
A function, that takes in a surface (the screen) and returns nothing.

All three types of these must also include a Z Order int, to render them in the correct order
"""
onion = typing.Union[
    tuple[tuple[pygame.Surface, pygame.Rect], int], 
    tuple[pygame.Surface, int], 
    tuple[typing.Callable[[pygame.Surface], None], int]
]
Renderable = typing.NewType("Renderable", onion) #ide marks this as error but it runs fine, unsure why

class MouseState():
    """
    Represents the mouse's current state
    """
    rmb: bool
    lmb: bool
    x: int
    y: int

    def __init__(self, mpos: tuple[int, int], mpress: tuple[bool, bool]) -> None:
        """
        Parameters
        ----------
        mpos: Tuple of two ints, representing the x/y position of the mouse.
        mpress: Tuple of two bools, representing if the left/right mouse buttons are pressed, respectively.
        """
        self.rmb = mpress[1]
        self.lmb = mpress[0]

        self.x = mpos[0]
        self.y = mpos[1]

class Instance():
    """
    The basic class representing any object in the game. Designed to be a superclass to other classes.
    """
    parent: Instance
    children: dict[str, Instance]
    renderables: dict[str, Renderable]

    def __init__(self, parent: Instance):
        self.parent = parent
        self.children = {}
        self.renderables = {}

    def update(self, events: list[pygame.event.Event], mouseState: MouseState, deltaTime: float):
        pass

    def add_child(self, cid: typing.Any, child: Instance):
        """Adds a child with a given ID. Sets the parent of the child to this instance."""
        self.children[cid] = child
        child._parent = self
        instanceCache.add(self.children[cid])
    
    def remove_child(self, cid: typing.Any):
        """Removes a child from this instance's children. If child does not exist, does nothing."""
        if cid not in self.children: return

        #recursively remove subchildren
        for child in list(self.children[cid].children.keys()):
            self.children[cid].remove_child(child)

        instanceCache.remove(self.children[cid])
        del self.children[cid]
        