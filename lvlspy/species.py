import numpy as np
import lvlspy.properties as lp
import lvlspy.level as lv
import lvlspy.transition as lt


class Species(lp.Properties):
    """A class for storing and retrieving data about a species.

    Args:
        ``name`` (:obj:`str`): The name of the species.

        ``levels`` (:obj:`list`, optional): A list of individual
        :obj:`lvlspy.level.Level` objects.

        ``transitions`` (:obj:`list`, optional): A list of individual
        :obj:`lvlspy.transition.Transition` objects.

        ``units`` (:obj:`str`, optional):  A string giving the
        units for the energy.

    """

    def __init__(self, name, levels=None, transitions=None):
        self.name = name
        self.levels = []
        self.transitions = []
        self.properties = {}
        if levels:
            for level in levels:
                self.levels.append(level)
        if transitions:
            for transition in transitions:
                self.transitions.append(transition)

    def get_name(self):
        """Retrieve the name of the species.

        Return:
            The :obj:`str` giving the species name.

        """

        return self.name

    def add_level(self, level):
        """Method to add a level to a species.

        Args:
            ``level`` (:obj:`lvlspy.level.Level`) The level to be added.

        Return:
            On successful return, the level has been added.

        """

        self.levels.append(level)

    def remove_level(self, level):
        """Method to remove a level from a species.

        Args:
            ``level`` (:obj:`lvlspy.level.Level`) The level to be removed.

        Return:
            On successful return, the level has been removed.

        """

        self.levels.remove(level)

    def add_transition(self, transition):
        """Method to add a transition to a species.

        Args:
            ``transition`` (:obj:`lvlspy.transition.Transition`) The transition
            to be added.

        Return:
            On successful return, the transition has been added.

        """

        self.transitions.append(transition)

    def remove_transition(self, transition):
        """Method to remove a transition from a species.

        Args:
            ``transition`` (:obj:`lvlspy.transition.Transition`) The transition
            to be removed.

        Return:
            On successful return, the transition has been removed.

        """

        self.transitions.remove(transition)

    def get_levels(self):
        """Method to retrieve the levels for a species.

        Returns:
            :obj:`list`: A list of the levels.  The levels are sorted in
            ascending energy.

        """

        return sorted(self.levels, key=lambda x: x.energy)

    def get_transitions(self):
        """Method to retrieve the transitions for a species.

        Returns:
            :obj:`list`: A list of the transitions.

        """

        return self.transitions

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

    def compute_rate_matrix(self, T):
        """Method to compute the rate matrix for a species.

        Args:
            ``T`` (:obj:`float`): The temperature in K at which to compute the
            rate matrix.

            Returns:
                :obj:`numpy.array`: A 2d numpy array giving the rate matrix.

        """

        levels = self.get_levels()

        rate_matrix = np.zeros((len(levels), len(levels)))

        transitions = self.get_transitions()

        for transition in transitions:
            i_upper = levels.index(transition.get_upper_level())
            i_lower = levels.index(transition.get_lower_level())

            r_upper_to_lower = transition.compute_upper_to_lower_rate(T)
            r_lower_to_upper = transition.compute_lower_to_upper_rate(T)

            rate_matrix[i_lower, i_upper] += r_upper_to_lower
            rate_matrix[i_upper, i_upper] -= r_upper_to_lower

            rate_matrix[i_upper, i_lower] += r_lower_to_upper
            rate_matrix[i_lower, i_lower] -= r_lower_to_upper

        return rate_matrix
