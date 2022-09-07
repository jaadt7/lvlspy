import numpy as np
import lvlspy.props as lp

class Species(lp.Properties):
    """A class for storing and retrieving data about a species.

    Args:
        ``name`` (:obj:`str`): The name of the species.

        ``levels`` (:obj:`list`, optional): A list of individual
        :obj:`lvlspy.level.Level` objects.

        ``units`` (:obj:`str`, optional):  A string giving the
        units for the energy.

    """

    def __init__(self, name):
        self.name = name
        self.levels = []
        self.properties = {}

    def __init__(self, name, levels):
        self.name = name
        self.levels = []
        self.properties = {}
        for level in levels:
            self.levels.append(level)

    def get_levels(self):
        """Method to retrieve the levels for a species.

        Returns:
            :obj:`list`: A list of the levels.  The levels are sorted in
            ascending energy.

        """

        return sorted(self.levels, key=lambda x: x.energy)
