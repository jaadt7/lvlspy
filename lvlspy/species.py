"""Module to handle species."""

import numpy as np
import lvlspy.properties as lp
import lvlspy.calculate as calc
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
        super().__init__()
        self.name = name
        self.levels = []
        self.transitions = []
        self.properties = {}
        if levels:
            for level in levels:
                self.levels.append(level)
        if transitions:
            for transition in transitions:
                self.add_transition(transition)

    def get_name(self):
        """Retrieve the name of the species.

        Return:
            The :obj:`str` giving the species name.

        """

        return self.name

    def update_name(self, name):
        """Change the name of the species.

        Args:
            ``name`` (:obj:`string`) The new name of the species

        Return:
            On successful return, the species' name has been updated
        """

        self.name = name

    def add_level(self, level):
        """Method to add a level to a species.

        Args:
            ``level`` (:obj:`lvlspy.level.Level`) The level to be added.

        Return:
            On successful return, the level has been added.  If the level
            previously existed in the species, it has been replaced with
            the new level.

        """

        if level in self.get_levels():
            self.remove_level(level)

        self.levels.append(level)

    def remove_level(self, level):
        """Method to remove a level from a species.

        Args:
            ``level`` (:obj:`lvlspy.level.Level`) The level to be removed.

        Return:
            On successful return, the level and all connected transitions have been removed.

        """
        for _l in self.get_upper_linked_levels(level):
            _t = self.get_level_to_level_transition(_l, level)
            if _t:
                self.remove_transition(_t)

        for _l in self.get_lower_linked_levels(level):
            _t = self.get_level_to_level_transition(level, _l)
            if _t:
                self.remove_transition(_t)

        self.levels.remove(level)

    def add_transition(self, transition):
        """Method to add a transition to a species.

        Args:
            ``transition`` (:obj:`lvlspy.transition.Transition`) The transition
            to be added.

        Return:
            On successful return, the transition has been added.  If the
            transition previously existed in the species, it has been
            replaced with the new transition.

        """

        if transition in self.get_transitions():
            self.remove_transition(transition)

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

    def get_lower_linked_levels(self, level):
        """Method to retrieve the lower-energy levels linked to the input level
        by transitions in the species.

        Args:
            ``level`` (:obj:`lvlspy.level.Level`) The level for which
            the linked levels are sought.

        Return:
            :obj:`list`: A list of the lower-energy levels linked to the
            input level by transitions.

        """

        result = []
        for transition in self.get_transitions():
            if transition.get_upper_level() == level:
                result.append(transition.get_lower_level())

        return result

    def get_upper_linked_levels(self, level):
        """Method to retrieve the higher-energy levels linked to the input level
        by transitions in the species.

        Args:
            ``level`` (:obj:`lvlspy.level.Level`) The level for which
            the linked levels are sought.

        Return:
            :obj:`list`: A list of the higher-energy levels linked to the
            input level by transitions.

        """

        result = []
        for transition in self.get_transitions():
            if transition.get_lower_level() == level:
                result.append(transition.get_upper_level())

        return result

    def get_level_to_level_transition(self, upper_level, lower_level):
        """Method to retrieve the downward transition from a particular
        upper level to a particular lower level.

        Args:
            ``upper_level`` (:obj:`lvlspy.level.Level`) The level from which
            the transition originates.

            ``lowerlevel`` (:obj:`lvlspy.level.Level`) The level to which
            the transition goes.

        Return:
            :obj:`lvlspy.transition.Transition`: The transition, or None
            if the transition is not found.

        """

        for transition in self.get_transitions():
            if (
                transition.get_upper_level() == upper_level
                and transition.get_lower_level() == lower_level
            ):
                return transition

        return None

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

    def compute_equilibrium_probabilities(self, temperature):
        """Method to compute the equilibrium probabilities for levels in a
        species.

        Args:
            ``temperature`` (:obj:`float`): The temperature in K at which to
            compute the equilibrium probabilities.

            Returns:
                :obj:`numpy.array`: A numpy array of the probabilities of the
                levels.  The levels are sorted in ascending energy.

        """

        levs = self.get_levels()

        prob = np.empty(len(levs))

        for i, lev in enumerate(levs):
            prob[i] = lev.compute_boltzmann_factor(temperature)

        prob /= np.sum(prob)

        return prob

    def compute_rate_matrix(self, temperature):
        """Method to compute the rate matrix for a species.

        Args:
            ``temperature`` (:obj:`float`): The temperature in K at which to
            compute the rate matrix.

            Returns:
                :obj:`numpy.array`: A 2d numpy array giving the rate matrix.

        """

        levels = self.get_levels()

        rate_matrix = np.zeros((len(levels), len(levels)))

        transitions = self.get_transitions()

        for transition in transitions:
            i_upper = levels.index(transition.get_upper_level())
            i_lower = levels.index(transition.get_lower_level())
            if (
                "useable" in levels[i_upper].get_properties()
                and levels[i_upper].get_properties()["useable"] is False
            ) or (
                "useable" in levels[i_lower].get_properties()
                and levels[i_lower].get_properties()["useable"] is False
            ):
                continue

            r_upper_to_lower = transition.compute_upper_to_lower_rate(
                temperature
            )
            r_lower_to_upper = transition.compute_lower_to_upper_rate(
                temperature
            )

            rate_matrix[i_lower, i_upper] += r_upper_to_lower
            rate_matrix[i_upper, i_upper] -= r_upper_to_lower

            rate_matrix[i_upper, i_lower] += r_lower_to_upper
            rate_matrix[i_lower, i_lower] -= r_lower_to_upper

        return rate_matrix

    def fill_missing_transitions(self, a):
        """Method to fill in transitions between levels using a Weisskopf estimate.
        Parity must be set as a property, otherwise method would return wrong estimates

        Args:
            `a` (:obj:`int`) Mass number of the species
        Returns:
            Upon successful return, the species will have an updated list of transitions
            based on Weisskopf estimate
        """

        levels = self.get_levels()
        for i in range(1, len(levels)):
            for j in range(i):
                t_dummy = self.get_level_to_level_transition(
                    levels[i], levels[j]
                )
                if t_dummy is None:

                    e = [levels[i].get_energy(), levels[j].get_energy()]
                    jj = [
                        int((levels[i].get_multiplicity() - 1) / 2),
                        int((levels[j].get_multiplicity() - 1) / 2),
                    ]
                    p = [
                        levels[i].get_properties()["parity"],
                        levels[j].get_properties()["parity"],
                    ]

                    p = self._set_parity(p)

                    ein_a = calc.Weisskopf().estimate(e, jj, p, a)

                    self.add_transition(
                        lt.Transition(levels[i], levels[j], ein_a)
                    )

    def fill_missing_ensdf(self, a):
        """Method to fill in missing transitions from either not listed in ENSDF
        or level with useable property flagged as false due to unclear J^pi

        Args:
            ``a`` (:obj:`int`) Mass number of species

        Returns:
            Upon successful return, the species would be updated with all transitions
        """

        levels = self.get_levels()
        for i in range(1, len(levels)):
            for j in range(i):
                if (
                    self.get_level_to_level_transition(levels[i], levels[j])
                    is None
                ):
                    ein_a = 0.0

                    jpi_i = levels[i].get_properties()["j^pi"]
                    jpi_j = levels[j].get_properties()["j^pi"]

                    e = [levels[i].get_energy(), levels[j].get_energy()]

                    if jpi_i == "" or jpi_j == "":

                        self.add_transition(
                            lt.Transition(levels[i], levels[j], ein_a)
                        )
                        continue

                    if (
                        levels[i].get_properties()["useability"] is False
                        and levels[j].get_properties()["useability"] is True
                    ):

                        self.add_transition(
                            lt.Transition(
                                levels[i],
                                levels[j],
                                self._get_ein_a_from_mixed_upper_level_to_lower(
                                    [e, ein_a, jpi_i, levels[j], a]
                                ),
                            )
                        )
                        continue

                    if (
                        levels[i].get_properties()["useability"] is True
                        and levels[j].get_properties()["useability"] is True
                    ):

                        jj = [
                            int((levels[i].get_multiplicity() - 1) / 2),
                            int((levels[j].get_multiplicity() - 1) / 2),
                        ]
                        p = [
                            levels[i].get_properties()["parity"],
                            levels[j].get_properties()["parity"],
                        ]
                        p = self._set_parity(p)
                        self.add_transition(
                            lt.Transition(
                                levels[i],
                                levels[j],
                                calc.Weisskopf().estimate(e, jj, p, a),
                            )
                        )
                        continue

                    if (
                        levels[i].get_properties()["useability"]
                        and levels[j].get_properties()["useability"] is False
                    ):

                        self.add_transition(
                            lt.Transition(
                                levels[i],
                                levels[j],
                                self._get_ein_a_to_mixed_lower_level(
                                    [e, ein_a, jpi_j, levels[i], a]
                                ),
                            )
                        )
                        continue

                    if (
                        levels[i].get_properties()["useability"] is False
                        and levels[j].get_properties()["useability"] is False
                    ):

                        self.add_transition(
                            lt.Transition(
                                levels[i],
                                levels[j],
                                self._get_ein_a_from_mixed_to_mixed(
                                    [e, ein_a, jpi_i, jpi_j, a]
                                ),
                            )
                        )
                        continue

    def _get_ein_a_from_mixed_to_mixed(self, in_list):
        jpi_i_range = self._get_jpi_range(in_list[2])
        jpi_j_range = self._get_jpi_range(in_list[3])
        for ki in jpi_i_range:
            for kj in jpi_j_range:
                jj = [int(ki[0]), int(kj[0])]
                p = [ki[1], kj[1]]
                p = self._set_parity(p)
                in_list[1] += (
                    calc.Weisskopf().estimate(in_list[0], jj, p, in_list[4])
                    / len(jpi_i_range)
                    / len(jpi_j_range)
                )

        return in_list[1]

    def _get_ein_a_to_mixed_lower_level(self, in_list):

        jpi_j_range = self._get_jpi_range(in_list[2])

        for k in jpi_j_range:
            jj = [int((in_list[3].get_multiplicity() - 1) / 2), int(k[0])]
            p = [in_list[3].get_properties()["parity"], k[1]]
            p = self._set_parity(p)
            in_list[1] += calc.Weisskopf().estimate(
                in_list[0], jj, p, in_list[4]
            ) / len(jpi_j_range)

        return in_list[1]

    def _get_ein_a_from_mixed_upper_level_to_lower(self, in_list):

        jpi_i_range = self._get_jpi_range(in_list[2])
        for k in jpi_i_range:
            jj = [int(k[0]), int((in_list[3].get_multiplicity() - 1) / 2)]
            p = [k[1], in_list[3].get_properties()["parity"]]
            p = self._set_parity(p)
            in_list[1] += calc.Weisskopf().estimate(
                in_list[0], jj, p, in_list[4]
            ) / len(jpi_i_range)
        return in_list[1]

    def _set_parity(self, p):
        if p[0] == "+":
            p[0] = 1
        else:
            p[0] = -1
        if p[1] == "+":
            p[1] = 1
        else:
            p[1] = -1
        return p

    def _get_jpi_range(self, jpi):

        # first strip any available parentheses
        jpi = jpi.replace("(", "")
        jpi = jpi.replace(")", "")
        j_range = []
        if jpi == "":
            return j_range
        if "TO" in jpi or ":" in jpi:
            p = jpi[-1]
            if "TO" in jpi:
                jpi = jpi.split("TO")
            if ":" in jpi:
                jpi = jpi.split(":")

            if "+" not in jpi and "-" not in jpi:
                p = "+"
            m1 = int(lp.Properties().evaluate_expression(jpi[0].strip(p)))
            m2 = int(lp.Properties().evaluate_expression(jpi[1].strip(p)))
            for i in range(m1, m2 + 1):
                j_range.append([i, p])

        else:
            if "OR" in jpi:
                jpi = jpi.split("OR")
            if "," in jpi:
                jpi = jpi.split(",")
            for j in jpi:
                if "+" not in j and "-" not in j:
                    m = int(2 * lp.Properties().evaluate_expression(j) + 1)
                    p = "+"
                    j_range.append([m, p])
                else:
                    p = j[-1]
                    m = int(
                        2 * lp.Properties().evaluate_expression(j[0:-1]) + 1
                    )
                    j_range.append([m, p])
        return j_range

    def evolve(self, temperature, y0, time=None, tol=1e-6):
        """Method to evolve levels at a given temperature

        Args:
            ``temperature`` (:obj:`float`) The temperature in K to evolve the system at.

            ``y0`` (:obj:`numpy.array`) The array containing the
            initial conditions of the level system.

            ``time`` (:obj:`numpy.array`, optional) The time array to evolve the system.
            Defaults to logspace between 1.e-30 and 100 at 200 steps

            ``tol`` (:obj:`float`, optional) The tolerance for the solver. Defaults to 1e-6

        Returns:
            ``y`` (:obj:`numpy.array`) A 2D numpy array of dimensions len(time)xlen(levels) of the
            evolved system
        """

        if time is None:
            time = np.logspace(np.log10(1.0e-30), np.log10(100), 200)

        y = np.empty((len(time), len(y0)))
        y[0, :] = y0
        rate_matrix = self.compute_rate_matrix(temperature)
        return calc.Evolution().newton_raphson(y, time, tol, rate_matrix)

    def evolve_csc(self, temp, y0, time):
        """
        Evolves the system using sparse solver

        Args:
            ``temp`` (:obj:`float`): The temperature in K

            ``y0`` (:obj:`numpy.array`): An array containing the initial conditions

            ``time`` (:obj:`numpy.array`): An array containing the time steps to evolve
            the system over

        Returns:
            Upon successful return, a 2D numpy array is returned containing the evolved system
        """

        rm = self.compute_rate_matrix(temp)
        return calc.Evolution().csc_solve(y0, rm, time)
