"""Base class for handling properties for all classes."""

import re


class Properties:
    """A class for storing and retrieving optional properties."""

    def __init__(self):
        self.properties = {}

    def get_properties(self):
        """Method to retrieve the optional properties.

        Returns:
            :obj:`dict`: The dictionary of current properties.

        """

        return self.properties

    def update_properties(self, properties):
        """Method to update the optional properties.

        Args:
            ``properties`` (:obj:`dict`):  A dictionary of properties.
            New properties are added.  Old properties are updated.

        Returns:
            On successful return, the properties have been updated.

        """

        self.properties = {**self.properties, **properties}

    def evaluate_expression(self, expression):
        """Method to extract range of jpi depending on ENSDF definition"""
        # Extract numbers and operators from the expression string
        elements = re.findall(r"(\d+|\+|\-|\*|\/)", expression)

        # Initialize the result to the first number
        result = int(elements[0])

        # Apply each operator to the previous result and the current number
        for i in range(1, len(elements), 2):
            operator = elements[i]
            num = int(elements[i + 1])
            if operator == "+":
                result += num
            elif operator == "-":
                result -= num
            elif operator == "*":
                result *= num
            elif operator == "/":
                result /= num

        return result

    def set_parity(self, p):
        """Method to transform partity from +/- string to +/- 1 integer"""
        if p[0] == "+":
            p[0] = 1
        else:
            p[0] = -1
        if p[1] == "+":
            p[1] = 1
        else:
            p[1] = -1
        return p
