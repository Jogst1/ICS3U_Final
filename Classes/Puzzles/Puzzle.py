from Classes.Puzzles.Testcase import Testcase

class Puzzle():
    """
    Represents a base puzzle for the game. This includes:
        Instructions and flavour text
        Inputs and expected outputs for the example testcase (which will be displayed in the editor)
        At least 3 (ideally more) test-cases including inputs and expected outputs for each
    """

    def __init__(self, instructions: str, example_testcase: Testcase, testcases: list[Testcase]):
        self.instructions = instructions
        self.example_testcase = example_testcase
        self.testcases = testcases