"""
Module to handle weisskopf calculations
"""

import numpy as np
import scipy.special as spc
from gslconsts.consts import GSL_CONST_NUM_ZETTA


def spin_from_multiplicity(multiplicity):
    """Return angular momentum J from the level multiplicity 2J + 1."""

    return (multiplicity - 1) / 2


def _multipole_range(spins):
    """Return the allowed integer photon multipoles for two level spins."""

    lower = max(1, abs(spins[0] - spins[1]))
    upper = spins[0] + spins[1]
    if not float(lower).is_integer() or not float(upper).is_integer():
        raise ValueError(
            "Level spins must both be integer or both be half-integer"
        )

    return range(int(lower), int(upper) + 1)


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
        for jj in _multipole_range(j):
            ein_a += self._get_rate(jj, p, e, a)

        return ein_a

    def estimate_from_ensdf(self, t, a):
        """
        Calculates the Weisskopf estimate for a transition between two states based on the
        properties available from the ENSDF file.

        Args:
            ``lvs`` (:obj:`lvlspy.core.level.Level`) The levels of the species

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
            spin_from_multiplicity(l_upp.get_multiplicity()),
            spin_from_multiplicity(l_low.get_multiplicity()),
        ]

        p = [
            l_upp.get_properties()["parity"],
            l_low.get_properties()["parity"],
        ]
        ein_a = 0.0
        j_range = _multipole_range(j)

        if "Reduced_Matrix_Coefficient" not in t.get_properties():
            for jj in j_range:
                ein_a += self._get_rate(jj, p, e, a)

        else:
            for jj in j_range:
                ein_a += self._get_adjusted_rate(jj, t, a)

        return ein_a

    def _get_adjusted_rate(self, jj, t, a):
        properties = t.get_properties()
        e = [
            t.get_upper_level().get_energy(),
            t.get_lower_level().get_energy(),
        ]
        p = [
            t.get_upper_level().get_properties()["parity"],
            t.get_lower_level().get_properties()["parity"],
        ]
        mixing_ratio = self._get_mixing_ratio(properties)

        if np.power(-1, jj) * p[0] == p[1]:
            b_1 = self._get_adjustment_factor(
                jj,
                properties,
                transition_kind="E",
                mixing_ratio=mixing_ratio,
            )
            if b_1 == 1.0:
                return self.rate_elec(e[0], e[1], jj, a) / 10

            return (
                self.rate_elec(e[0], e[1], jj, a) * b_1 / self._b_sp_el(a, jj)
            )

        b_1 = self._get_adjustment_factor(
            jj,
            properties,
            transition_kind="M",
            mixing_ratio=mixing_ratio,
        )
        if b_1 == 1.0:
            return self.rate_mag(e[0], e[1], jj, a) / 10

        return self.rate_mag(e[0], e[1], jj, a) * b_1 / self._b_sp_ml(a, jj)

    def _get_mixing_ratio(self, properties):
        mixing_ratio = properties.get("Mixing_Ratio", 0.0)
        if mixing_ratio == "":
            return 0.0
        return float(mixing_ratio)

    def _get_adjustment_factor(
        self, jj, properties, transition_kind, mixing_ratio
    ):
        b_1 = 1.0
        rmc_type_1 = properties.get("tran_1_type", "")
        rmc_type_2 = properties.get("tran_2_type", "")
        rmc_val_1 = properties.get("tran_1_val", 1.0)
        rmc_val_2 = properties.get("tran_2_val", 1.0)

        if transition_kind in rmc_type_1 and str(jj) in rmc_type_1:
            b_1 = rmc_val_1

        if transition_kind in rmc_type_2 and str(jj) in rmc_type_2:
            b_1 = rmc_val_2

        if mixing_ratio != 0.0:
            if transition_kind == "E":
                b_1 = (
                    b_1
                    * np.power(mixing_ratio, 2)
                    / (1.0 + np.power(mixing_ratio, 2))
                )
            else:
                b_1 = b_1 / (1.0 + mixing_ratio**2)

        return b_1

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

    def _b_sp_ml(self, a, j):
        return (
            10.0
            * np.power(3.0 / (j + 3.0), 2)
            * np.power(1.2 * a ** (1 / 3), 2 * j - 2)
            / np.pi
        )

    def _b_sp_el(self, a, j):
        return (
            np.power(3.0 / (3.0 + j), 2)
            * np.power(1.2 * np.power(a, 1 / 3), 2 * j)
            / (4 * np.pi)
        )
