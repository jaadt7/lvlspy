"""Module for handling transitions."""
import numpy as np
from gslconsts.consts import (
    GSL_CONST_CGSM_ELECTRON_VOLT,
    GSL_CONST_CGS_PLANCKS_CONSTANT_H,
    GSL_CONST_CGS_SPEED_OF_LIGHT,
    GSL_CONST_CGSM_BOLTZMANN,
)
import lvlspy.properties as lp


class Transition(lp.Properties):
    """A class for storing and retrieving data about a transition.

    Args:
        ``upper_level`` (:obj:`lvlspy.level.Level`) The level from which
        there is a spontaneous decay.

        ``lower_level`` (:obj:`lvlspy.level.Level`) The level to which
        there is a spontaneous decay.

        ``einstein_A`` (:obj:`float`): The Einstein A coefficient
        (the spontaneous decay rate per second from `upper_level` to
        `lower_level`).

    """

    def __init__(self, upper_level, lower_level, einstein_a):
        super().__init__()
        self.properties = {}
        self.upper_level = upper_level
        self.lower_level = lower_level
        self.einstein_a = einstein_a

    def __eq__(self, other):
        if not isinstance(other, Transition):
            return NotImplemented

        return (
            self.upper_level == other.upper_level
            and self.lower_level == other.lower_level
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

    def get_einstein_a(self):
        """Method to retrieve the Einstein A coefficient for the transition.

        Returns:
            :obj:`float`: The spontaneous rate (per second) for the transition.

        """

        return self.einstein_a

    def update_einstein_a(self, einstein_a):
        """Method that updates the Einstein A coefficient of a transition.

        Args:
            ``transition`` (:obj:`lvlspy.transition.Transition`) The
            transition to be modified.

            ``einstein_A`` (:obj:`float`) The new value for the Einstein A
            coefficient.

        Returns:
            On successful return, the transition Einstein A coefficient
            has been updated.
        """

        self.einstein_a = einstein_a

    def get_einstein_b_upper_to_lower(self):
        """Method to get the Einstein B coefficient for the upper level
        to lower level transition (induced emission).

        Returns:
            :obj:`float`: The Einstein coefficient in cm :sup:`2`
            steradian per erg per s.

        """

        result = self.einstein_a / self._fnu()

        return result

    def get_einstein_b_lower_to_upper(self):
        """Method to get the Einstein B coefficient for the lower level
        to upper level transition (induced absorption).

        Returns:
            :obj:`float`: The Einstein coefficient in cm :sup:`2`
            steradian per erg per s.

        """

        return self.get_einstein_b_upper_to_lower() * (
            self.upper_level.get_multiplicity()
            / self.lower_level.get_multiplicity()
        )

    def compute_lower_to_upper_rate(self, temperature, user_func=None):
        """Method to compute the total rate for transition from the lower
        level to upper level.

        Args:
            ``temperature`` (:obj:`float`) The temperature in K at which to
            compute the rate.

            ``user_func`` (optional): A `function
            <https://docs.python.org/3/library/stdtypes.html#functions>`_
            that computes the lower level to upper level transition rate.
            If supplied, the routine will use this function in place of the
            default one, which computes the rate from the appropriate
            Einstein coefficient and the blackbody spectrum.
            The function must take one :obj:`float` argument giving the
            temperature. Other data can be bound to the function.

        Returns:
            :obj:`float`: The rate (per second).

        """

        if user_func:
            return user_func(temperature)

        return self.get_einstein_b_lower_to_upper() * self._bb(temperature)

    def compute_upper_to_lower_rate(self, temperature, user_func=None):
        """Method to compute the total rate for transition from the upper
        level to to lower level.

        Args:
            ``temperature`` (:obj:`float`) The temperature in K at which to
            compute the rate.

            ``user_func`` (optional): A `function
            <https://docs.python.org/3/library/stdtypes.html#functions>`_
            that computes the upper level to lower level transition rate.
            If supplied, the routine will use this function in place of the
            default one, which computes the rate from the appropriate
            Einstein coefficients and the blackbody spectrum.
            The function must take one :obj:`float` argument giving the
            temperature. Other data can be bound to the function.

        Returns:
            :obj:`float`: The rate (per second).

        """

        if user_func:
            return user_func(temperature)

        return (
            self.get_einstein_a()
            + self.get_einstein_b_upper_to_lower() * self._bb(temperature)
        )

    def get_frequency(self):
        """Method to compute the frequency of the transition.

        Returns:
            :obj:`float`: The frequency (in Hz) of the transition.

        """

        delta_e = self.upper_level.get_energy() - self.lower_level.get_energy()

        delta_e_erg = (1e3) * delta_e * GSL_CONST_CGSM_ELECTRON_VOLT

        return delta_e_erg / GSL_CONST_CGS_PLANCKS_CONSTANT_H

    def _fnu(self):
        return (
            2.0
            * GSL_CONST_CGS_PLANCKS_CONSTANT_H
            * np.power(self.get_frequency(), 3)
            / np.power(GSL_CONST_CGS_SPEED_OF_LIGHT, 2)
        )

    def _bb(self, temperature):
        k_bt = GSL_CONST_CGSM_BOLTZMANN * temperature

        delta_e = self.upper_level.get_energy() - self.lower_level.get_energy()

        x_p = delta_e * 1.0e3 * GSL_CONST_CGSM_ELECTRON_VOLT / k_bt

        if x_p < 500:
            return self._fnu() / np.expm1(x_p)
        return self._fnu() * np.exp(-x_p)
