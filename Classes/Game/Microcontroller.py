import pygame
import math

#set up some generael use constants
surf=pygame.display.get_surface()
MICROCONTROLLER_IMAGE = pygame.image.load("Assets/Game/microcontroller.png").convert_alpha(surf)
MICROCONNECTOR_IMAGE = pygame.image.load("Assets/Game/Wires/micro_connector.png").convert_alpha(surf)
FONT_12PT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 12)
FONT_16PT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 16)
TEXT_OFFSET = (270 - 230, 10)

#set up some constants for validating code lines
COMMANDS = {
    "mov": 2,
    "jmp": 1,
    "slp": 1,
    "add": 1,
    "sub": 1,
    "mul": 1,
    "tis": 2,
    "tgt": 2,
    "tlt": 2
}
REGISTERS = [
    "in1",
    "ou1",
    "in2",
    "ou2",
    "mhs",
    "ics"
]
NUMBERS = [str(i) for i in range(1000)]
CONDITIONALS = [
    "+",
    "-"
]


def line_is_valid(line: str) -> bool:
    """
    Checks if a provided line of code is a valid M.H.S. instruction.
    """
    line = line.lower().strip()
    words = line.split(" ")
    command = ""

    #guard clause to allow just whitespace lines, but not single-word commands as there are none
    if len(words) < 2:
        return line == "" or line == " " #todo: make this better at detecting whitespace (maybe use .strip?)

    #if the first "word" is not in the command list
    if words[0] not in COMMANDS.keys():
        #if the first "word" is a conditional
        if words[0] in CONDITIONALS:
            #set the command to the seocnd "word"
            command = words[1]
            #set the words to be only the remaining args
            words = words[2:]
        #if it is just plain not a valid command
        else:
            #lien isnt valid
            return False
    #if first word is a command
    else:
        #set the command to be the first 'word'
        command = words[0]
        #set the words to be only the remaining args
        words = words[1:]
        
    #get the number of arguments associated with the command
    num_args = COMMANDS[command]

    #if the remaining "words" hjave a different length than the number of arguments, line is invalid
    if len(words) != num_args: return False

    #check that all arguments are either a valid number or register.
    for word in words:
        if word not in REGISTERS and word not in NUMBERS:
            return False
    
    #if we have gotten here, the line is valid
    return True


class Microcontroller(pygame.sprite.Sprite):
    """
    Represents a Microcontroller, capable of being programmed, and running M.H.S. code.
    """

    def __init__(self, position: tuple[int]):
        super().__init__()

        #set up a surf and rect for rendering
        self.surf = MICROCONTROLLER_IMAGE
        self.rect = self.surf.get_rect()
        self.rect.topleft = position

        #set up a rect to contain text
        self.text_rect = pygame.Rect((position[0] + TEXT_OFFSET[0], position[1] + TEXT_OFFSET[1]), (160, 160))

        #set up some variables to keep track of lines, input, typing, and errors
        self.lines = [""] * 10
        self.current_line = 0
        self.typing = False
        self.line_errors = set()


        #set up some variables to represent register values
        self.in1 = 0
        self.ou1 = 0
        self.in2 = 0
        self.ou2 = 0
        self.mhs = 0
        self.ics = 0

        #set up some variables to keep track of meta microcontroller state
        self.sleep_counter = 1
        self.current_sim_line = 0
        self.conditional_state = None

        # define functions for each M.H.S. instruction
        def mov(src, dst):
            #if trying to mov into a number, do nothing, because that makes no sense
            if isinstance(dst, int):
                return
            
            if "in" in dst:
                return

            if isinstance(src, str):
                self.__dict__[dst] = self.__dict__[src]
            else:
                self.__dict__[dst] = src
        def jmp(dst):
            jmp_line = min(dst if isinstance(dst, int) else self.__dict__[dst], 9)
            self.current_line = jmp_line
        def slp(amt):
            cycles_to_sleep = amt if isinstance(amt, int) else self.__dict__[amt]
            self.sleep_counter = cycles_to_sleep
        def add(amt):
            add_amt = amt if isinstance(amt, int) else self.__dict__[amt]
            self.mhs += add_amt
            self.mhs = self.mhs % 1000 #loop back over on "int overflows" (not actually an overflow just thought thisd be neat to have lol)
        def sub(amt):
            sub_amt = amt if isinstance(amt, int) else self.__dict__[amt]
            self.mhs -= sub_amt
            self.mhs = self.mhs % 1000 # allow for underflows
        def mul(amt):
            mul_amt = amt if isinstance(amt, int) else self.__dict__[amt]
            self.mhs *= mul_amt
            self.mhs = self.mhs % 1000
        def tis(x, y):
            x = self.__dict__[x] if isinstance(x, str) else x
            y = self.__dict__[x] if isinstance(x, str) else x

            self.conditional_state = x==y
        def tgt(x, y):
            x = self.__dict__[x] if isinstance(x, str) else x
            y = self.__dict__[x] if isinstance(x, str) else x

            self.conditional_state = x>y
        def tlt(x, y):
            x = self.__dict__[x] if isinstance(x, str) else x
            y = self.__dict__[x] if isinstance(x, str) else x

            self.conditional_state = x<y


        #set up an object to map command strings to their associated functions
        self.command_handler = {
            "mov": mov,
            "jmp": jmp,
            "slp": slp,
            "add": add,
            "sub": sub,
            "mul": mul,
            "tis": tis,
            "tgt": tgt,
            "tlt": tlt
        }

        #update the surface to display initial register data
        self.update_surf()
        

    def update(self, events: list[pygame.event.Event]):
        """
        Given a list of pygame events, update the microcontroller. Handles user input, typing, etc.
        """

        # if left mouse is pressed
        if pygame.mouse.get_pressed()[0]:
            #and mouse position is inside the text rect
            if self.text_rect.collidepoint(*pygame.mouse.get_pos()):
                #calculate the line that the mouse is hovering on, and set the current line to it
                self.current_line = math.floor((pygame.mouse.get_pos()[1] - self.text_rect.topleft[1]) / 16)
                #enable typing
                self.typing = True
            else:
                #disable typing
                self.typing = False

        #if typing is enabled
        if self.typing:
            for event in events:
                #if a key got pressed
                if event.type == pygame.KEYDOWN:
                    #if key is delete or backspace, remove one character from the current line
                    if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        self.lines[self.current_line] = self.lines[self.current_line][:-1]
                    
                    #if key is enter/return, go to next line
                    elif event.key == pygame.K_RETURN:
                        self.current_line += 1
                        #if there are no more lines, stop typing
                        if self.current_line > 9:
                            self.typing = False

                    #if key is e or q, stop typing, as no instructions/registers have these characters, and they are used for managing miccrocontrollers
                    elif event.key == pygame.K_e or event.key == pygame.K_q:
                        self.typing = False
                    
                    #if key is anything else, add it's unicode representation to the current line
                    else:
                        self.lines[self.current_line] += event.unicode

                    #check if the new edited line is valid, and if it is, add it to the line_errors, otherwise remove it.
                    if line_is_valid(self.lines[self.current_line]):
                        self.line_errors.discard(self.current_line)
                    else:
                        self.line_errors.add(self.current_line)

                    #update the surface to display the new line data
                    self.update_surf()

    def update_surf(self):
        """
        Updates the microcontroller's render surface to display text and register values
        """
        self.surf = MICROCONTROLLER_IMAGE.copy()

        #render text lines
        for i, line in enumerate(self.lines):
            textrender = FONT_12PT.render(line, True, (0, 0, 0))
            rect = textrender.get_rect()
            rect.topleft = (TEXT_OFFSET[0], TEXT_OFFSET[1] + (16 * i))
            self.surf.blit(textrender, rect)

        #render a red line under all error lines
        for line_error in self.line_errors:
            pygame.draw.line(self.surf, (204, 34, 0), (TEXT_OFFSET[0], TEXT_OFFSET[1] - 2 + (line_error + 1) * 16), (TEXT_OFFSET[0]+160, TEXT_OFFSET[1] - 2 + (line_error + 1) * 16), 2)

        #render mhs register value
        mhs_textrender = FONT_16PT.render(str(self.mhs), True, (0, 0, 0))
        mhs_rect = mhs_textrender.get_rect()
        mhs_rect.midtop = (205+25, 15 + 25)
        self.surf.blit(mhs_textrender, mhs_rect)
        
        #render ics register value
        ics_textrender = FONT_16PT.render(str(self.ics), True, (0, 0, 0))
        ics_rect = ics_textrender.get_rect()
        ics_rect.midtop = (205+25, 15 + 25 + 100)
        self.surf.blit(ics_textrender, ics_rect)
            
    def do_sim_tick(self):
        """
        Does a simulation tick, updating the Microcontroller's values.
        """

        #decrement sleep counter
        self.sleep_counter -= 1
        #if sleep counter is still above 0, sleep for longer
        if self.sleep_counter > 0:
            return
        elif self.sleep_counter < 0:
            self.sleep_counter = 0
        
        stored_mhs = self.mhs
        stored_ics = self.ics

        max_counter = 50 #make sure the simulation doesn't loop forever, like in the case of an empty microcontroller or one devoid of a slp statement
        while self.sleep_counter == 0 and max_counter > 0:
            max_counter -= 1

            #if current line is an error, skip it
            if self.current_sim_line in self.line_errors:
                print(f"Skipped line {self.current_line} because it was an error")
                self.current_sim_line = (self.current_sim_line + 1) % 10
                continue
            
            line = self.lines[self.current_sim_line].lower().strip()

            #if current line is whitespace, skip it
            if line.isspace() or line == "":
                self.current_sim_line = (self.current_sim_line + 1) % 10
                continue

            #if current line has a conditional and the condition fails, skip it
            if line[0] in CONDITIONALS:
                conditional = False if line[0] == "-" else True
                line = line[2:]
                if self.conditional_state != conditional:
                    self.current_sim_line = (self.current_sim_line + 1) % 10
                    continue
            
            #get the command and arguments
            words = line.split(" ")
            command = words[0]
            args = [int(arg) if arg.isdigit() else arg for arg in words[1:]]

            #call command, and increment the linecounter
            self.command_handler[command](*args)
            self.current_sim_line = (self.current_sim_line + 1) % 10


        #if mhs or ics values have changed during this tick, we need to update the render surface
        if stored_ics != self.ics or stored_mhs != self.mhs:
            self.update_surf()

        

class MicroPointer(pygame.sprite.Sprite):
    """
    A class to occupy grid spaces, that points to a microcontroller, and stores information about its respective port id
    Also handles rendering of wires connecting other wires to the microcontroller
    """
    def __init__(self, pointTo: tuple[int, int], portId: str):
        super().__init__()
        self.pointTo = pointTo
        self.portId = portId

        self.surf = MICROCONNECTOR_IMAGE.copy()
        self.rect = self.surf.get_rect()

        self.connected = False

        if self.portId != None and "2" in self.portId:
            self.surf = pygame.transform.rotate(self.surf, 180)

        self.surf.set_alpha(0)

    def set_connected(self, flag: bool):
        self.connected = flag
        self.surf.set_alpha(256 * int(flag))

    def to_modifier(self) -> tuple[int, int]:
        if self.portId == None: return (0, 0)
        return (-1, 0) if "1" in self.portId else (1, 0)