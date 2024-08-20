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
        Calculates the transition rate between two levels where the transition
          is a magnetic multipole

        Args:
            ``e_i'' (:obj: `float') Energy of the initial state (in keV)
            ``e_f'' (:obj: `float') Energy of the final state (in keV)
            ``j''   (:obj: `int')   Angular momentum of the gamma ray
            ``a''   (:obj: `int')   Mass number


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
        Calculates the transition rate between two levels where
        the transition is an electric multipole

        Args:
            ``e_i'' (:obj: `float') Energy of the initial state (in keV)
            ``e_f'' (:obj: `float') Energy of the final state (in keV)
            ``j''   (:obj: `int')   Angular momentum of the gamma ray
            ``a''   (:obj: `int')   Mass number


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

    def estimate_from_ensdf(self, lvs, tran, a):
        """
        Calculates the Weisskopf estimate for a transition between two states.

        Args:
            ``lvs'' (:obj:`lvlspy.level.Level`) The levels of the species
            ``tran'' (:obj: `list') An array containing all the data from ENSDF
            regarding a single transition
        Returns:
            ``ein_a'' (:obj:`float') The total estimate for the transition rate
            (in per second) using Weisskopf single partice estimate
        """

        #e_i = lvs[tran[0]].get_energy()  # upper energy level
        #e_f = lvs[tran[1]].get_energy()  # lower energy level
        e = [lvs[tran[0]].get_energy(),lvs[tran[1]].get_energy()]
        #j_i = (lvs[tran[0]].get_multiplicity() - 1) / 2  # J of upper level
        #j_f = (lvs[tran[1]].get_multiplicity() - 1) / 2  # J of lower level
        j = [(lvs[tran[0]].get_multiplicity() - 1) / 2,
             (lvs[tran[1]].get_multiplicity() - 1) / 2]
        #p_i = lvs[tran[0]].get_properties()["parity"]  # upper level parity
        #p_f = lvs[tran[1]].get_properties()["parity"]  # lower level parity
        p = [lvs[tran[0]].get_properties()["parity"],lvs[tran[1]].get_properties()["parity"]]
        ein_a = 0

        if p_i == "+":
            p_i = 1
        else:
            p_i = -1

        if p_f == "+":
            p_f = 1
        else:
            p_f = -1

        j = range(
            max(1, abs(int(j_i - j_f))), j_i + j_f
        )  # range of gamma angular momenta
        m_r = 0
        if tran[6] != "":
            m_r = float(tran[6])  # mixing ratio

        b = self._get_reduced_trans_prob(tran[15])
        i_e = np.where(np.strings.find(b, "E") == 1)[0][0]
        i_b = np.where(np.strings.find(b, "M") == 1)[0][0]
        if tran[15] == "":
            for jj in j:
                if np.power(-1, jj) * p_i == p_f:
                    ein_a += (
                        self.rate_elec(e_i, e_f, jj, a) / 10
                    )  # Weisskopf estimates in generally over-estimate by a factor of 10
                else:
                    ein_a += self.rate_mag(e_i, e_f, jj, a) / 10
        else:
            for jj in j:
                b_1 = 1
                if np.power(-1, jj) * p_i == p_f:
                    if b[i_e][1] == "E" and int(b[i_e][2]) == jj:
                        b_1 = float(b[i_e][5 : len(b[i_e])])
                        if b[i_e][1:3] == "E2" and tran[6] != "":
                            b_1 = (
                                b_1
                                * np.power(m_r, 2)
                                / (1.0 + np.power(m_r, 2))
                            )
                    ein_a += (
                        self.rate_elec(e_i, e_f, jj, a) * b_1
                    )  # Weisskopf estimates in generally over-estimate by a factor of 10
                else:
                    if b[i_b][1] == "M" and int(b[i_b][2]) == jj:
                        b_1 = float(b[i_b][5 : len(b[i_b])])
                        if b[i_b][1:3] == "M1" and tran[6] != "":
                            b_1 = b_1 / (1.0 + np.power(m_r, 2))
                    ein_a += self.rate_mag(e_i, e_f, jj, a) * b_1

        return ein_a

    def _get_reduced_trans_prob(self, mod_b):
        reduced_prob = []
        mods = mod_b.split("$")
        if mod_b == "":
            reduced_prob.append(mod_b)
            return reduced_prob

        if len(mods) == 1:
            sp_mods = mods[0].split()

            if len(sp_mods[2]) > 4:
                reduced_prob.append(sp_mods[2])
            else:
                reduced_prob.append(sp_mods[2] + "=" + sp_mods[4])
        else:
            for i,m in enumerate(mods):
                sp_mods = m.split()
                if i == 0:
                    if len(sp_mods[2]) > 4:
                        reduced_prob.append(sp_mods[2])
                    else:
                        reduced_prob.append(sp_mods[2] + "=" + sp_mods[4])
                else:
                    if len(sp_mods[0]) > 4:
                        reduced_prob.append(sp_mods[0])
                    else:
                        reduced_prob.append(sp_mods[0] + "=" + sp_mods[2])

        return reduced_prob
