
class Testcase():
    """
    Represents a testcase for a puzzle. A test-case contains a series of inputs, and expected outputs. All values should be between 0-999 inclusive
    """
    def __init__(self, inputs: list[int], expected_outputs: list[int], inputs2: list[int]=None, expected_outputs2: list[int]=None):
        """
        Parameters
        ----------
        inputs:
            A list of inputs, between 0 and 999
        expected_outputs:
            A list of expected outputs, between 0 and 999
        inputs2 (optional):
            A second list of inputs, between 0 and 999
        expected_outputs2:
            A list of expected outputs, between 0 and 999
        """
        if inputs2 == None:
            inputs2 = [0]*len(inputs)
            expected_outputs2 = [0]*len(expected_outputs)

        #ensure the lists are the same length, raise error if not
        if len(inputs) != len(expected_outputs):
            raise ValueError("The inputs and expected_outputs lists should be of the same length!")
        
        #ensure all elements are between 0-999 inclusive, raise error if not
        for value_list, name in zip(
            [
                inputs, inputs2, expected_outputs, expected_outputs2
            ],
            [
                "inputs", "inputs2", "expected_outputs", "expected_outputs2"
            ]
        ):
            for index, value in enumerate(value_list):
                if value < 0:
                    raise ValueError(f"{name} list element at index {index} was smaller than 0. Elements must be between 0-999 inclusive.")
                elif value > 999:
                    raise ValueError(f"{name} list element at index {index} was greater than 999. Elements must be between 0-999 inclusive.")

        self.inputs = inputs
        self.inputs2 = inputs2
        self.expected_outputs = expected_outputs
        self.expected_outputs2 = expected_outputs2