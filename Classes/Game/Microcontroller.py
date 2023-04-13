import pygame
import math

MICROCONTROLLER_IMAGE = pygame.image.load("Assets/Game/microcontroller.png").convert_alpha(pygame.display.get_surface())
FONT = pygame.font.Font("Assets/Fonts/IBMPlexMono-Medium.ttf", 12)

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
            textrender = FONT.render(line, True, (0, 0, 0))
            rect = textrender.get_rect()
            rect.topleft = (TEXT_OFFSET[0], TEXT_OFFSET[1] + (16 * i))
            self.surf.blit(textrender, rect)
        for line_error in self.line_errors:
            pygame.draw.line(self.surf, (204, 34, 0), (TEXT_OFFSET[0], TEXT_OFFSET[1] - 2 + (line_error + 1) * 16), (TEXT_OFFSET[0]+160, TEXT_OFFSET[1] - 2 + (line_error + 1) * 16), 2)
            

class MicroPointer():
    def __init__(self, pointTo, portId):
        self.pointTo = pointTo
        self.portId = portId