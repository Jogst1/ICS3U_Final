import pygame
from Classes.Instance import Instance
from Util.Assets import Assets

class TextRenderer(Instance):
    """
    Renders text. Handles word-wrapping and newlines.
    """
    def __init__(
            self, 
            parent: Instance, 
            text: str, 
            color: tuple[int, int, int], 
            font: pygame.font.Font, 
            rect: pygame.Rect,
            zIndex:int=1
    ):
        super().__init__(parent)

        self.renderables["main"] = (
            (pygame.Surface(rect.size, pygame.SRCALPHA),
            rect),
            zIndex
        )

        self.font = font
        self.color = color
        self.set_text(text)
        
    def set_text(self, text: str):
        """
        Set or change the text the textrenderer is displaying.
        """
        #determine the dimensions of any character in the font, this will only work with monospace fonts (which this project exclusively uses)
        font_width, font_height = self.font.size("a")

        #get a list of words in the text, reversed to allow them to be gradually `.pop`ped in the right order
        words = text.split(" ")[::-1]
        #set up a list to keep track of the different lines
        lines = []
        #buffer for the current line
        current_line = ""

        #loop until there are no words left
        while len(words) > 0:
            #get the next word
            word = words.pop()
            #if the word added to the current line is still within the bounds of the rect
            if "\n" in word:
                subwords = word.split("\n")
                current_line = current_line + subwords[0]
                lines.append(current_line)
                current_line = subwords[1] + " "

            elif len(current_line+word)*font_width < self.renderables["main"][0][1].width:
                #add the word to the current line, followed by a space
                current_line = current_line+word + " "
            else:
                #add the current line to the lines list, and start fresh with a buffer just co
                lines.append(current_line)
                current_line = word+" "
        #add the current (final) line to the list
        lines.append(current_line)
        
        #clear the display surface by filling it with a fully transparent color
        self.renderables["main"][0][0].fill((0, 0, 0, 0))
        #loop over the lines with their number, using enumerate
        for lineNum, line in enumerate(lines):
            #render the line, with antialiasing and the provided color
            render = self.font.render(line, True, self.color)
            #position it at the right place in the display, adjusted for the line number
            render_rect = render.get_rect()
            render_rect.topleft = (
                0,
                font_height * lineNum
            )
            #blit the line to the display
            self.renderables["main"][0][0].blit(render, render_rect)
