import numpy as np
import lvlspy.props as lp
import lvlspy.level as lv


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

    def compute_equilibrium_probabilities(self, T):
        """Method to compute the equilibrium probabilities for levels in a species.

        Args:
            ``T`` (:obj:`float`): The temperature in K at which to compute the
            equilibrium probabilities.

            Returns:
                :obj:`numpy.array`: A numpy array of the probabilities of the levels.
                The levels are sorted in ascending energy.

        """

        levs = self.get_levels()

        p = np.empty(len(levs))

        for i in range(len(levs)):
            p[i] = levs[i].compute_Boltzmann_factor(T)

        p /= np.sum(p)

        return p
