"""
Module to handle weisskopf calculations
"""

import numpy as np
import scipy.special as spc
from gslconsts.consts import GSL_CONST_NUM_ZETTA


class Weisskopf:
    """
    A class for handling Weisskopf related calculations
    """

    def rate_mag(self, e_i, e_f, j, a):
        """
        Calculates the transition rate between two levels where the transition is a magnetic multipole

        Args:
        - e_i: energy of the initial state (in keV)
        - e_f: energy of the final state (in keV)
        - j  : the angular momentum of the state
        - a  : mass number


        Returns:
        - The magnetic contribution to the Weisskopf estimate between the two states
        """

        de = e_i - e_f

        s = (
            2 * (j + 1) / (j * np.power(spc.factorial2(2 * j + 1), 2))
        ) * np.power(3 / (j + 3), 2)

        return (
            0.55
            * s
            * np.power(a, -2 / 3)
            * np.power(de / 197000.0, 2 * j + 1)
            * np.power(1.4 * np.power(a, 1.0 / 3.0), 2 * j)
            * GSL_CONST_NUM_ZETTA
        )

    def rate_elec(self, e_i, e_f, j, a):
        """
        Calculates the transition rate between two levels where the transition is an electric multipole

        Args:
        - e_i: energy of the initial state (in keV)
        - e_f: energy of the final state (in keV)
        - j  : the angular momentum of the state
        - a  : mass number


        Returns:
        - The electric contribution to the Weisskopf estimate between the two states
        """

        de = e_i - e_f  # energy difference

        s = (
            2 * (j + 1) / (j * np.power(spc.factorial2(2 * j + 1), 2))
        ) * np.power(3 / (j + 3), 2)

        return (
            2.4
            * s
            * np.power(de / 197000.0, 2 * j + 1)
            * np.power(1.4 * np.power(a, 1.0 / 3.0), 2 * j)
            * GSL_CONST_NUM_ZETTA
        )

    def estimate_from_ensdf(self, lvs, tran):
        e_i = lvs[tran[0]].get_energy()  # upper energy level
        e_f = lvs[tran[1]].get_energy()  # lower energy level

        j_i = (lvs[tran[0]].get_multiplicity() - 1) / 2  # J of upper level
        j_f = (lvs[tran[1]].get_multiplicity() - 1) / 2  # J of lower level

        p_i = lvs[tran[0]].get_properties()["parity"]  # upper level parity
        p_f = lvs[tran[1]].get_properties()["parity"]  # lower level parity

        if p_i == "+":
            p_i = 1
        else:
            p_i = -1

        if p_f == "+":
            p_f = 1
        else:
            p_f = -1

        return
