#import libs
import random
#import classes
from Classes.Puzzles.Testcase import Testcase
from Classes.Puzzles.Puzzle import Puzzle

#set up a consistent random number generator to allow for consistent puzzle testcases
random.seed(10)

puzzles = []

def puzzle1_testcase():
    in1 = [0] * 50
    in2 = [0] * 50
    for i in range(20):
        in1[random.randrange(0, 50)] = 1
    for i in range(10):
        in2[random.randrange(0, 50)] = 1
    ou1 = []
    ou2 = [0] * 50
    score = 0
    for i in range(50):
        score += in1[i]
        score -= in2[i]*2
        if score < 0:
            score += in2[i]*2
            in2[i] = 0
        ou1.append(score)

    return Testcase(
        in1, ou1, in2, ou2
    )
    
puzzle1 = Puzzle(
    "The Marauders are playing a new and inventive sport, and need a device to keep score. They want two buttons that range in values from (0 - 1), one for a point, and one for a penalty. The device should keep track of score, and decrement its score twice for a penalty. Input 1 should be used for score, Input 2 for penalty, Output 1 for score.",
    puzzle1_testcase(),
    [puzzle1_testcase() for _ in range(5)]
)
puzzles.append(puzzle1)

def puzzle2_testcase():
    inps = []
    oups = []

    blocks = [
        (random.randint(2, 6), random.randint(1, 4))
        for _ in range(3)
    ]
    for block in blocks:
        inps.extend([0]*block[1])
        inps.extend([1]*block[0])

    inps.extend([0]*(30-len(inps)))

    flag = False
    for i in range(len(inps)):
        flag = not flag
        oups.append(int(flag and bool(inps[i])))

    return Testcase(
        inps,
        oups
    )
puzzle2 = Puzzle(
    "The Marauders need a button-controlled buzzer for their games. They asked you to make a device that pulses on or off, but only outputs while the buzzer button is being pressed. The button is represented by Input 1, which is either 0 or 1, and the buzzer output is Output 1, and should be either 0 or 1.",
    puzzle2_testcase(),
    [puzzle2_testcase() for _ in range(10)]
)
puzzles.append(puzzle2)

def puzzle3_testcase():
    out = []
    nm1 = 1 #ics
    nm2 = 0 #in1/ou1
    for _ in range(15):
        v = nm1 + nm2
        out.append(v)
        nm2 = nm1
        nm1 = v
    return Testcase(
        [0] * 15,
        out
    )
puzzle3 = Puzzle(
    "Some students in math class are having trouble understanding the Fibonacci sequence, and need some help. Make a device that outputs the fibonacci sequence, omitting the first term. As a reminder, fib(n) = fib(n - 1) + fib(n - 2), and the first two terms are 1 and 1.\n \n(HINT): Loop a wire back into its source microcontroller...",
    puzzle3_testcase(),
    []
)
# sol'n https://i.imgur.com/zQNQlmS.png

PUZZLE4_WANTED_LEN = 30
def puzzle4_testcase():
    input1 = []
    input2 = []
    output1 = []
    
    while len(input1) < PUZZLE4_WANTED_LEN:
        start_block_length = random.randint(0, 2)
        input1.extend([0] * start_block_length)
        input2.extend([0] * start_block_length)
        output1.extend([0] * start_block_length)
        block_length = random.randint(2, 7)
        input1.append(block_length)
        pitch = random.randint(1, 99)
        input2.append(pitch)
        input1.extend([0] * block_length)
        input2.extend([0] * block_length)
        output1.extend([0] * block_length)
        output1.append(pitch)

    if len(input1) % 2 != 0:
        input1.append(0)
        input2.append(0)
        output1.append(0)

    return Testcase(
        input1,output1,input2,[0]*len(input1)
    )

puzzle4 = Puzzle(
    "A student has asked you to design a timer for helping them practice their sprinting in gym class. Whenever Input 1 contains a value, set a timer with the length being that value. On the same tick, Input 2 will contain the desired pitch of the timer. Once the timer is up, output the desired pitch to Output 1 for a single tick.",

    puzzle4_testcase(),
    [puzzle4_testcase() for _ in range(5)]
)
puzzles.append(puzzle4)

#this is arguably harder so add it last
puzzles.append(puzzle3)