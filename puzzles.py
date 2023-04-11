#import classes
from Classes.Puzzles.Testcase import Testcase
from Classes.Puzzles.Puzzle import Puzzle

puzzle1 = Puzzle(
    "Example Puzzle 1! Add one to the input",
    Testcase(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ),
    [
        Testcase(
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        ),
        Testcase(
            [20, 31, 42, 53, 64, 75, 86, 97, 8, 10],
            [21, 32, 43, 54, 65, 76, 87, 98, 9, 11]
        ),
    ]
)