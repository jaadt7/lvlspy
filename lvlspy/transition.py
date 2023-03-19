import numpy as np
import lvlspy.properties as lp
from gslconsts.consts import *


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

    def __eq__(self, other):
        if not isinstance(other, Transition):
            return NotImplemented

        return (
            self.upper_level == other.upper_level
            and self.lower_level == other.lower_level
            and self.Einstein_A == other.Einstein_A
        )

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

    def get_Einstein_B_upper_to_lower(self):
        """Method to get the Einstein B coefficient for the upper level
        to lower level transition (induced emission).

        Returns:
            :obj:`float`: The Einstein coefficient in cm\ :sup:`2`
            steradian per erg per s.

        """

        nu = self.get_frequency()

        result = self.Einstein_A / self._fnu()

        return result

    def get_Einstein_B_lower_to_upper(self):
        """Method to get the Einstein B coefficient for the lower level
        to upper level transition (induced absorption).

        Returns:
            :obj:`float`: The Einstein coefficient in cm\ :sup:`2`
            steradian per erg per s.

        """

        return self.get_Einstein_B_upper_to_lower() * (
            self.upper_level.get_multiplicity() / self.lower_level.get_multiplicity()
        )

    def compute_lower_to_upper_rate(self, T):
        """Method to compute the total rate for transition from the lower level to
        upper level.

        Args:
            ``T`` (:obj:`float`:) The temperature in K at which to compute
            the rate.

        Returns:
            :obj:`float`: The rate (per second).

        """

        return self.get_Einstein_B_lower_to_upper() * self._bb(T)

    def compute_upper_to_lower_rate(self, T):
        """Method to compute the total rate for transition from the upper level to
        to lower level.

        Args:
            ``T`` (:obj:`float`:) The temperature in K at which to compute
            the rate.

        Returns:
            :obj:`float`: The rate (per second).

        """

        return self.get_Einstein_A() + self.get_Einstein_B_upper_to_lower() * self._bb(
            T
        )

    def get_frequency(self):
        """Method to compute the frequency of the transition.

        Returns:
            :obj:`float`: The frequency (in Hz) of the transition.

        """

        deltaE = self.upper_level.get_energy() - self.lower_level.get_energy()

        deltaE_erg = (1e3) * deltaE * GSL_CONST_CGS_ELECTRON_VOLT

        return deltaE_erg / GSL_CONST_CGS_PLANCKS_CONSTANT_H

    def _fnu(self):
        return (
            2.0
            * GSL_CONST_CGS_PLANCKS_CONSTANT_H
            * np.power(self.get_frequency(), 3)
            / np.power(GSL_CONST_CGS_SPEED_OF_LIGHT, 2)
        )

    def _bb(self, T):
        k_BT = GSL_CONST_CGSM_BOLTZMANN * T

        deltaE = self.upper_level.get_energy() - self.lower_level.get_energy()

        x = deltaE * 1.0e3 * GSL_CONST_CGSM_ELECTRON_VOLT / k_BT

        if x < 500:
            return self._fnu() / np.expm1(x)
        else:
            return self._fnu() * np.exp(-x)
