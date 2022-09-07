import numpy as np
import lvlspy.props as lp

class Transition(lp.Properties):
    """A class for storing and retrieving data about a transition.

    Args:
        ``upper_level`` (:obj:`lvlspy.level.Level`) The level from which
        there is a spontaneous decay.

        ``lower_level`` (:obj:`lvlspy.level.Level`) The level to which
        there is a spontaneous decay.

        ``Einstein_A`` (:obj:`float`): The Einstein A coefficient (the spontaneous
        decay rate per second from `upper_level` to `lower_level`).

    """

    def __init__(self, upper_level, lower_level, Einstein_A):
        self.properties = {}
        self.upper_level = upper_level
        self.lower_level = lower_level
        self.Einstein_A = Einstein_A

    def get_upper_level(self):
        """Method to retrieve the `upper_level` for the transition.

        Returns:
            :obj:`lvlspy.level.Level`: The `upper_level` for the transition.

        """

        return self.upper_level

    def get_lower_level(self):
        """Method to retrieve the `lower_level` for the transition.

        Returns:
            :obj:`lvlspy.level.Level`: The `lower_level` for the transition.

        """

        return self.lower_level

    def get_Einstein_A(self):
        """Method to retrieve the Einstein A coefficient for the transition.

        Returns:
            :obj:`float`: The spontaneous rate (per second) for the transition.

        """

        return self.Einstein_A

    def compute_Einstein_B_upper_to_lower(self, T):
        """Method to compute the Einstein B coefficient for the upper level
        to lower level transition (induced emission).

        Args:
            ``T`` (:obj:`float`:) The temperature in K at which to compute
            the coefficient.

        Returns:
            :obj:`float`: The Einstein coefficient.

        """

#       Do the computation.  Return in cgs units.

    def compute_Einstein_B_lower_to_upper(self, T):
        """Method to compute the Einstein B coefficient for the lower level
        to upper level transition (induced absorption).

        Args:
            ``T`` (:obj:`float`:) The temperature in K at which to compute
            the coefficient.

        Returns:
            :obj:`float`: The Einstein coefficient.

        """

#       Do the computation.  Return in cgs units.

    def compute_lower_to_upper_rate(self, T):
        """Method to compute the total rate for transition from the lower level to
        upper level.

        Args:
            ``T`` (:obj:`float`:) The temperature in K at which to compute
            the coefficient.

        Returns:
            :obj:`float`: The rate (per second).

        """

#       Do the computation.  Return in per second.

    def compute_upper_to_lower_rate(self, T):
        """Method to compute the total rate for transition from the upper level to
        to lower level.

        Args:
            ``T`` (:obj:`float`:) The temperature in K at which to compute
            the coefficient.

        Returns:
            :obj:`float`: The rate (per second).

        """

#       Do the computation.  Return in per second.

