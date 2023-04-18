import pygame
import math

MICROCONTROLLER_IMAGE = pygame.image.load("Assets/Game/microcontroller.png").convert_alpha(pygame.display.get_surface())
FONT_12PT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 12)
FONT_16PT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 16)

TEXT_OFFSET = (270 - 230, 10)

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
NUMBERS = [str(i) for i in range(100)]
CONDITIONALS = [
    "+",
    "-"
]

def line_is_valid(line: str) -> bool:
    line = line.lower().strip()
    words = line.split(" ")
    command = ""

    #guard clause to allow just whitespace lines, but not single-word commands as there are none
    if len(words) < 2:
        return line == "" or line == " " #todo: make this better at detecting whitespace (maybe use .strip?)

    if words[0] not in COMMANDS.keys():
        if words[0] in CONDITIONALS:
            command = words[1]
            words = words[2:]
        else:
            return False
    else:
        command = words[0]
        words = words[1:]
        
    num_args = COMMANDS[command]

    if len(words) != num_args: return False

    for word in words:
        if word not in REGISTERS and word not in NUMBERS:
            return False
        
    return True


class Microcontroller(pygame.sprite.Sprite):

    def __init__(self, position: tuple[int]):
        super().__init__()

        self.surf = MICROCONTROLLER_IMAGE
        self.rect = self.surf.get_rect()
        self.rect.topleft = position

        self.text_rect = pygame.Rect((position[0] + TEXT_OFFSET[0], position[1] + TEXT_OFFSET[1]), (160, 160))

        self.lines = [""] * 10
        self.current_line = 0
        self.typing = False
        self.line_errors = set()

        self.in1 = 0
        self.ou1 = 0
        self.in2 = 0
        self.ou2 = 0

        self.mhs = 0
        self.ics = 0

        self.sleep_counter = 1
        self.current_sim_line = 0
        self.conditional_state = None


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

        self.update_surf()
        

    def update(self, events: list[pygame.event.Event]):
        if pygame.mouse.get_pressed()[0]:
            if self.text_rect.collidepoint(*pygame.mouse.get_pos()):
                self.current_line = math.floor((pygame.mouse.get_pos()[1] - self.text_rect.topleft[1]) / 16)
                self.typing = True
            else:
                self.typing = False

        if self.typing:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        self.lines[self.current_line] = self.lines[self.current_line][:-1]
                    elif event.key == pygame.K_RETURN:
                        self.current_line += 1
                        if self.current_line > 9:
                            self.typing = False

                    elif event.key == pygame.K_e or event.key == pygame.K_q:
                        self.typing = False
                    else:
                        self.lines[self.current_line] += event.unicode

                    if line_is_valid(self.lines[self.current_line]):
                        self.line_errors.discard(self.current_line)
                    else:
                        self.line_errors.add(self.current_line)
                    self.update_surf()

    def update_surf(self):
        self.surf = MICROCONTROLLER_IMAGE.copy()
        for i, line in enumerate(self.lines):
            textrender = FONT_12PT.render(line, True, (0, 0, 0))
            rect = textrender.get_rect()
            rect.topleft = (TEXT_OFFSET[0], TEXT_OFFSET[1] + (16 * i))
            self.surf.blit(textrender, rect)
        for line_error in self.line_errors:
            pygame.draw.line(self.surf, (204, 34, 0), (TEXT_OFFSET[0], TEXT_OFFSET[1] - 2 + (line_error + 1) * 16), (TEXT_OFFSET[0]+160, TEXT_OFFSET[1] - 2 + (line_error + 1) * 16), 2)

        mhs_textrender = FONT_16PT.render(str(self.mhs), True, (0, 0, 0))
        mhs_rect = mhs_textrender.get_rect()
        mhs_rect.midtop = (205+25, 15 + 25)
        self.surf.blit(mhs_textrender, mhs_rect)
        
        ics_textrender = FONT_16PT.render(str(self.ics), True, (0, 0, 0))
        ics_rect = ics_textrender.get_rect()
        ics_rect.midtop = (205+25, 15 + 25 + 100)
        self.surf.blit(ics_textrender, ics_rect)
            
    def do_sim_tick(self):
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
            
            words = line.split(" ")
            command = words[0]
            args = [int(arg) if arg.isdigit() else arg for arg in words[1:]]

            self.command_handler[command](*args)
            self.current_sim_line = (self.current_sim_line + 1) % 10


        if stored_ics != self.ics or stored_mhs != self.mhs:
            self.update_surf()

        

            

            

        



class MicroPointer():
    def __init__(self, pointTo, portId):
        self.pointTo = pointTo
        self.portId = portId