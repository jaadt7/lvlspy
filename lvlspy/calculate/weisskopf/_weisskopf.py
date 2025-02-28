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
        Calculates the transition rate between two levels where
        the transition is a magnetic multipole

        Args:
            ``e_i`` (:obj:`float`) Energy of the initial state (in keV)

            ``e_f`` (:obj:`float`) Energy of the final state (in keV)

            ``j``   (:obj:`int`)   Angular momentum of the gamma ray

            ``a``   (:obj:`int`)   Mass number


        Returns:
            The magnetic contribution to the Weisskopf estimate between the two states
        """

        de = e_i - e_f

        s = (
            1.9 * (j + 1) / (j * np.power(spc.factorial2(2 * j + 1), 2))
        ) * np.power(3 / (j + 3), 2)

        return (
            s
            * np.power(de / 197000.0, 2 * j + 1)
            * np.power(1.2 * np.power(a, 1.0 / 3.0), 2 * j - 2)
            * GSL_CONST_NUM_ZETTA
        )

    def rate_elec(self, e_i, e_f, j, a):
        """Calculates the transition rate between two levels where
        the transition is an electric multipole.

        Args:
            ``e_i`` (:obj:`float`) Energy of the initial state (in keV)

            ``e_f`` (:obj:`float`) Energy of the final state (in keV)

            ``j``   (:obj:`int`)   Angular momentum of the gamma ray

            ``a``   (:obj:`int`)   Mass number


        Returns:
            The electric contribution to the Weisskopf estimate between the two states
        """

        de = e_i - e_f  # energy difference

        s = (
            4.4 * (j + 1) / (j * np.power(spc.factorial2(2 * j + 1), 2))
        ) * np.power(3 / (j + 3), 2)

        return (
            s
            * np.power(de / 197000.0, 2 * j + 1)
            * np.power(1.2 * np.power(a, 1.0 / 3.0), 2 * j)
            * GSL_CONST_NUM_ZETTA
        )

    def estimate(self, e, j, p, a):
        """Calculates the Weisskopf estimate for a transition between two states.

        Args:
            ``e`` (:obj:`list`) An array containing the energies of the two levels

            ``j`` (:obj:`list`) An array containing the angular momenta of the two levels

            ``p`` (:obj:`list`) An array containing the parity of both levels

            ``a`` (:obj:`int`) The mass number of the species

        Returns:
            ``ein_a`` (:obj:`float`) The Einstein A coefficient of the downwards transition
        """
        ein_a = 0.0
        sm = j[0] + j[1]
        df = j[0] - j[1]
        j_range = range(
            max(1, abs(df)), sm + 1
        )  # range of gamma angular momenta

        for jj in j_range:
            ein_a += self._get_rate(jj, p, e, a)

        return ein_a

    def estimate_from_ensdf(self, t, a):
        """
        Calculates the Weisskopf estimate for a transition between two states based on the
        properties available from the ENSDF file.

        Args:
            ``lvs`` (:obj:`lvlspy.level.Level`) The levels of the species

            ``tran`` (:obj:`list`) An array containing all the data from
            ENSDF regarding a single transition

        Returns:
            ``ein_a`` (:obj:`float`) The total estimate for the transition rate
            (in per second) using Weisskopf single particle estimate
        """

        l_upp = t.get_upper_level()
        l_low = t.get_lower_level()

        e = [l_upp.get_energy(), l_low.get_energy()]
        j = [
            (l_upp.get_multiplicity() - 1) // 2,
            (l_low.get_multiplicity() - 1) // 2,
        ]
        if a % 2 != 0:
            j = [
                (l_upp.get_multiplicity() - 1) / 2,
                (l_low.get_multiplicity() - 1) / 2,
            ]

        p = [
            l_upp.get_properties()["parity"],
            l_low.get_properties()["parity"],
        ]
        ein_a = 0.0
        j_range = range(
            int(max(1, abs(j[0] - j[1]))), int(j[0] + j[1] + 1)
        )  # range of gamma angular momenta

        if t.get_properties()["Reduced_Matrix_Coefficient"] == "":
            for jj in j_range:
                ein_a += self._get_rate(jj, p, e, a)

        else:
            for jj in j_range:

                ein_a += self._get_adjusted_rate(jj, p, e, t, a)

        return ein_a

    def _get_adjusted_rate(self, jj, p, e, t, a):

        mixing_ratio = t.get_properties()["Mixing_Ratio"]
        if "tran_1_type" in t.get_properties():
            rmc_type_1 = t.get_properties()["tran_1_type"]
            rmc_val_1 = t.get_properties()["tran_1_val"]
        if "tran_2_type" in t.get_properties():
            rmc_type_2 = t.get_properties()["tran_1_type"]
            rmc_val_2 = t.get_properties()["tran_2_val"]

        b_1 = 1.0

        if np.power(-1, jj) * p[0] == p[1]:
            if "E" in rmc_type_1 and str(jj) in rmc_type_1:
                b_1 = rmc_val_1

            if (
                "E" in rmc_type_2
                and str(jj) in rmc_type_2
                and "tran_2_type" in t.get_properties()
            ):
                b_1 = rmc_val_2
            if mixing_ratio != "":
                mixing_ratio = float(mixing_ratio)
                b_1 = (
                    b_1
                    * np.power(mixing_ratio, 2)
                    / (1.0 + np.power(mixing_ratio, 2))
                )
            if b_1 == 1.0:
                return self.rate_elec(e[0], e[1], jj, a) / 10

            return (
                self.rate_elec(e[0], e[1], jj, a) * b_1 / self._b_sp_el(a, jj)
            )

        if "M" in rmc_type_1 and str(jj) in rmc_type_1:
            b_1 = rmc_val_1
        if (
            "M" in rmc_type_2
            and str(jj) in rmc_type_2
            and "tran_2_type" in t.get_properties()
        ):
            b_1 = rmc_val_2
        if mixing_ratio != "":
            mixing_ratio = float(mixing_ratio)
            b_1 = b_1 / (1.0 + np.power(mixing_ratio, 2))

        if b_1 == 1.0:
            return self.rate_mag(e[0], e[1], jj, a) / 10

        return self.rate_mag(e[0], e[1], jj, a) * b_1 / self._b_sp_ml(jj)

    def _get_rate(self, jj, p, e, a):

        if np.power(-1, jj) * p[0] == p[1]:
            return (
                self.rate_elec(e[0], e[1], jj, a) / 10
            )  # Weisskopf estimates in generally over-estimate by a factor of 10

        return (
            self.rate_mag(e[0], e[1], jj, a) / 10
        )  # Weisskopf estimates in generally over-estimate by a factor of 10

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
            for i, m in enumerate(mods):
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

    def _b_sp_ml(self, j):
        return (
            10.0 * np.power(3.0 / (j + 3.0), 2) * np.power(1.2, j - 1) / np.pi
        )

    def _b_sp_el(self, a, j):
        return (
            np.power(3.0 / (3.0 + j), 2)
            * np.power(1.2 * np.power(a, 1 / 3), 2 * j)
            / (4 * np.pi)
        )
