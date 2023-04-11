class Testcase():
    """
    Represents a testcase for a puzzle. A test-case contains a series of inputs, and expected outputs. All values should be between 1-99 inclusive
    """
    def __init__(self, inputs: list[int], expected_outputs: list[int]):
        """
        Parameters
        ----------
        inputs:
            A list of inputs, between 1 and 99
        expected_outputs:
            A list of expected outputs, between 1 and 99
        """
        #ensure the lists are the same length, raise error if not
        if len(inputs) != len(expected_outputs):
            raise ValueError("The inputs and expected_outputs lists should be of the same length!")
        
        #ensure all elements are between 1-99 inclusive, raise error if not
        for index, value in enumerate(inputs):
            if value < 1:
                raise ValueError(f"Input list element at index {index} was smaller than 1. Elements must be between 1-99 inclusive.")
            if value > 99:
                raise ValueError(f"Input list element at index {index} was greater than 99. Elements must be between 1-99 inclusive.")
        for index, value in enumerate(expected_outputs):
            if value < 1:
                raise ValueError(f"Expected outputs list element at index {index} was smaller than 1. Elements must be between 1-99 inclusive.")
            if value > 99:
                raise ValueError(f"Expected outputs list element at index {index} was greater than 99. Elements must be between 1-99 inclusive.")

        self.inputs = inputs
        self.expected_outputs = expected_outputs