#import classes
from Classes.Puzzles.Testcase import Testcase
from Classes.Puzzles.Puzzle import Puzzle

puzzle1 = Puzzle(
    "Example Puzzle 1! Add one to input 1, then multiply by four. Output the result to output 1",
    Testcase(
        list(range(1, 11)),
        [(x + 1) * 4 for x in range(1, 11)] 
    ),
    [
        Testcase(
            list(range(21, 31)),
            [(x + 1) * 4 for x in range(21, 31)] 
        ),
        Testcase(
            list(range(46, 56)),
            [(x + 1) * 4 for x in range(46, 56)] 
        ),
        Testcase(
            list(range(101, 151)),
            [(x + 1) * 4 for x in range(101, 151)] 
        ),
    ]
)