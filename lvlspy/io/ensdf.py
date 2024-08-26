"""
Module to handle ENSDF input and output
"""

import re
import math

import lvlspy.level as lv
import lvlspy.species as ls
import lvlspy.transition as lt
import lvlspy.calculate as calc


class ENSDF:
    """
    A class for handling the reading from and writing to ENSDF
    """

    def update_from_ensdf(self, coll, file, sp):
        """Method to update a species collection from an ENSDF file.

        Args:
            ``coll`` (:obj: `obj') The collection to be read from the ENSDF file

            ``file`` (:obj: `str`) The file name to update from.

            ``sp`` (:obj: `str`): The species to be read from file.


        Returns:
            On successful return, the species collection has been updated.

        """

        self._get_species_from_ensdf(coll, file, sp)

    def _set_level_properties(self, levels):
        properties = [
            "parity",
            "energy uncertainty",
            "j^pi",
            "isomer state",
            "half life",
            "half life uncertainty",
            "angular momentum transfer",
            "spectroscopic strength",
            "spectroscopic strength uncertainty",
            "Comment flag",
            "questionable character",
            "useability",
        ]
        levs = []
        for i, l in enumerate(levels):  # setting the level with properties

            levs.append(lv.Level(l[0], l[1]))
            additional_properties = [
                {key: value} for key, value in zip(properties, l[2:-1])
            ]
            additional_properties.append({properties[-1]: l[-1]})

            for j in additional_properties:
                levs[i].update_properties(j)

        return levs

    def _get_species_from_ensdf(self, coll, file, sp):
        match = re.search(r"\d+", sp)
        a = int(match.group())  # mass number

        identifiers = self._get_file_sp_and_identifiers(match, sp, a)

        levels, transitions = self._get_level_and_transition_data(
            file, identifiers
        )

        # setting the levels and transitions in lvlspy format
        levs = self._set_level_properties(levels)
        s = ls.Species(sp, levels=levs)

        lvs = s.get_levels()

        for tran in enumerate(transitions):
            if tran[1][1] == -1:
                continue

            if (
                lvs[tran[1][1]].get_properties()["useability"] is False
                or lvs[tran[1][0]].get_properties()["useability"] is False
            ):
                ein_a = 0
                t = lt.Transition(lvs[tran[1][0]], lvs[tran[1][1]], ein_a)
                t = self._set_transition_properties(t, tran[1])
                s.add_transition(t)
            else:
                ein_a = calc.Weisskopf().estimate_from_ensdf(lvs, tran[1], a)
                t = lt.Transition(lvs[tran[1][0]], lvs[tran[1][1]], ein_a)
                t = self._set_transition_properties(t, tran[1])
                s.add_transition(t)

        coll.add_species(s)

    def _set_transition_properties(self, t, tran):
        properties = [
            "E_gamma",
            "Delta_E",
            "Relative_Total_Intensity",
            "Relative_Total_Intensity_Uncertainty",
            "Transition_Multipolarity",
            "Mixing_Ratio",
            "Mixing_Ratio_Uncertainty",
            "Total_Conversion_Coefficient",
            "Total_Conversion_Coefficient_Uncertainty",
            "Relative_Total_Transition_Intensity",
            "Relative_Total_Transition_Intensity_Uncertainty",
            "Comment",
            "Coincidence",
            "Question",
            "Reduced_Matrix_Coefficient",
        ]
        add_properties = [
            {key: value} for key, value in zip(properties, tran[2:-1])
        ]
        for j in add_properties:
            t.update_properties(j)
        return t

    def _get_additional_level_properties(self, line):
        delta_e = line[19:21].strip()  # energy uncertainty
        jpi = line[21:39].strip()  # strip the spaces
        iso = line[77:79].strip()  # isomer indicator
        t_half = line[39:49].strip()  # level half life
        delta_t_half = line[49:55].strip()  # half life uncertainty
        l = line[55:64].strip()  # Angular momentum transfer
        s = line[64:74].strip()  # spectroscopic strength
        delta_s = line[74:76].strip()  # uncertainty in S
        comment = line[76]  # comment flag
        q = line[79]  # questionable level
        return [
            delta_e,
            jpi,
            iso,
            t_half,
            delta_t_half,
            l,
            s,
            delta_s,
            comment,
            q,
        ]

    def _get_additional_gamma_properties(self, line):
        delta_energy = line[19:21].strip()  # gamma energy uncertainty
        ri = line[21:29].strip()  # relative photon intensity
        dri = line[29:31].strip()  # uncertainty in RI
        m = line[31:41].strip()  # multipolarity of transition
        mr = line[41:49].strip()  # mixing ratio
        dmr = line[49:55].strip()  # uncertainty in MR
        cc = line[55:62].strip()  # Total conversion coefficient
        dcc = line[62:64].strip()  # uncertainty in CC
        ti = line[64:74].strip()  # relative total intensity
        dti = line[74:76].strip()  # uncertainty in TI
        c = line[76]  # comment flag
        coin = line[77]  # coincidence flag
        q = line[79]  # questions transition existance

        return [
            delta_energy,
            ri,
            dri,
            m,
            mr,
            dmr,
            cc,
            dcc,
            ti,
            dti,
            c,
            coin,
            q,
        ]

    def _read_levels(self, line, a, zero_counter):
        energy = line[9:19].strip()
        temp = []
        if energy[0] in a:
            str_dummy = energy[0] + "+"
            energy = energy.replace(str_dummy, "")
        if energy[-1] in a:
            str_dummy = "+" + energy[-1]
            energy = energy.replace(str_dummy, "")

        energy = float(energy)  # strip the spaces and cast to float
        if energy == 0.0:
            zero_counter += 1
        if zero_counter == 2:
            return temp, zero_counter

        properties = self._get_additional_level_properties(line)
        multi, parity, useable = self._extract_multi_parity(properties[1])

        temp = [
            energy,
            multi,
            parity,
        ]  # temporary dummy array for re-use
        for prop in enumerate(properties):
            temp.append(prop[1])
        temp.append(useable)

        return temp, zero_counter

    def _read_transition(self, line, a, lvls):
        e_g = line[9:19].strip()  # gamma ray energy

        if e_g[0] in a:
            str_dummy = e_g[0] + "+"
            e_g = e_g.replace(str_dummy, "")
        if e_g[-1] in a:
            str_dummy = "+" + e_g[0]
            e_g = e_g.replace(str_dummy, "")

        if e_g.isalpha() or e_g == "":
            e_g = str(0)

        e_g = float(e_g)
        index = -1
        for i, lev in enumerate(lvls):

            if math.isclose(
                abs(e_g - (lvls[-1][0] - lev[0])),
                0.0,
                abs_tol=1.0,
            ):
                index = i
                break

        temp = [len(lvls) - 1, index, e_g]
        properties = self._get_additional_gamma_properties(line)
        for prop in enumerate(properties):
            temp.append(prop[1])
        temp.append("")
        return temp

    def _get_level_and_transition_data(self, file, identifiers):

        lvls = (
            []
        )  # lvls format is (energy, multiplicity, parity, rest of properties)
        trans = []  # trans format is (top level, bottom level, reduced matrix)

        a = ["X", "Y", "Z", "U", "V", "W", "A", "B"]

        zero_counter = (
            0  # zero counter required as to only read in the adopted values
        )
        with open(file, "r", encoding="utf-8") as f:

            for line in f:
                # reading in level

                if line.startswith(identifiers[0]):
                    temp, zero_counter = self._read_levels(
                        line, a, zero_counter
                    )
                    lvls.append(temp)

                if zero_counter == 2:
                    lvls.pop(-1)
                    break

                # reading in gamma info

                if line.startswith(identifiers[1]):
                    temp = self._read_transition(line, a, lvls)
                    trans.append(temp)

                if line.startswith(identifiers[2]):
                    trans[-1][-1] = line

        return lvls, trans

    def _extract_multi_parity(self, jpi):
        """
        Takes jpi as the input and extracts the j and the parity and calculates the multiplicity

        Args:

             ``jpi'' (:obj: `str'): specifies the j and parity of the level

        Returns:
            ``multi'' (:obj: `int') : the multiplicity of the level. If multiplicity not clearly
            defined in ENSDF, will default to 10000
            ``parity'' (:obj: `str'): the parity of the level
            `` useable'' (:obj: `bool'): boolean if the level is useable or not depending
            on if jpi clearly defined

        """
        # first strip any available parentheses
        jpi = jpi.replace("(", "")
        jpi = jpi.replace(")", "")

        if jpi == "" or "TO" in jpi or "," in jpi or ":" in jpi or "OR" in jpi:
            multi = 10000
            parity = "+"
            useable = False

        else:
            if "+" not in jpi and "-" not in jpi:
                parity = "+"
                multi = int(2 * self._evaluate_expression(jpi) + 1)
                useable = True
            else:
                parity = jpi[-1]
                multi = int(2 * self._evaluate_expression(jpi[0:-1]) + 1)
                useable = True

        return multi, parity, useable

    def _get_file_sp_and_identifiers(self, match, sp, a):

        file_sp = (
            str(a) + sp.replace(match.group(), "").upper()
        )  # species string found in ENSDF file

        # retrieving species identifier to loop over in ENSDF file
        if len(match.group()) == 1:
            identifier = "  " + file_sp

        elif len(match.group()) == 2:
            identifier = " " + file_sp

        else:
            identifier = file_sp

        sym_len = len(sp.replace(match.group(), ""))

        if sym_len == 1:

            l_identifier = identifier + "   L"  # level identifier
            g_identifier = identifier + "   G"  # gamma transition identifier

        else:

            l_identifier = identifier + "  L"  # level identifier
            g_identifier = identifier + "  G"  # gamma transition identifier

        b_identifier = (
            identifier + "B "
        )  # reduced transition probability identifier

        return [l_identifier, g_identifier, b_identifier]

    def _evaluate_expression(self, expression):
        # Extract numbers and operators from the expression string
        elements = re.findall(r"(\d+|\+|\-|\*|\/)", expression)

        # Initialize the result to the first number
        result = int(elements[0])

        # Apply each operator to the previous result and the current number
        for i in range(1, len(elements), 2):
            operator = elements[i]
            num = int(elements[i + 1])
            if operator == "+":
                result += num
            elif operator == "-":
                result -= num
            elif operator == "*":
                result *= num
            elif operator == "/":
                result /= num

        return result

    def write_to_ensdf(self, coll, file):
        """
        Method that writes a collection of species to ENSDF format

        Args:
            ``coll`` (:obj: `lvlspy.spcoll.SpColl`) The collection to be written to file.
            Each species in the collection must have the species' name, level and gamma
             properties must be within ENSDF spec

        Returns:
            On successful return, the species collection has been written
        """
        for sp in coll.get():
            with open(file, "a", encoding="utf-8") as f:

                match = re.search(r"\d+", sp)
                a = int(match.group())  # mass number
                identifiers = self._get_file_sp_and_identifiers(match, sp, a)
                levels = coll.get()[sp].get_levels()
                for lev in levels:
                    line = self._construct_level_line(lev, identifiers)
                    f.write(line + "\n")
                    linked_levels = coll.get()[sp].get_lower_linked_levels(lev)
                    if linked_levels != []:
                        for l_lev in linked_levels:
                            transition = coll.get()[
                                sp
                            ].get_level_to_level_transition(lev, l_lev)
                            line = self._construct_gamma_line(
                                transition, identifiers
                            )
                            f.write(line + "\n")

    def _construct_level_line(self, lev, identifiers):
        energy = lev.get_energy()
        properties = lev.get_properties()

        props = {
            "energy_uncertainty": [19, 21],
            "j^pi": [21, 39],
            "half life": [39, 49],
            "half life uncertainty": [49, 55],
            "angular momentum transfer": [55, 64],
            "spectroscopic strength": [64, 74],
            "spectroscopic strength uncertainty": [74, 76],
            "Comment flag": [76],
            "isomer state": [77, 79],
            "questionable character": [79],
        }

        s = " " * 80
        s = identifiers[0] + s[8:]
        s = s[:9] + str(energy).center(19 - 9) + s[19:]
        for key, indices in props.items():
            if key in properties and len(indices) == 2:
                s = (
                    s[: indices[0]]
                    + str(properties[key]).center(indices[1] - indices[0])
                    + s[indices[1] :]
                )
            if key in properties and len(indices) == 1:
                s = (
                    s[: indices[0]]
                    + str(properties[key])
                    + s[indices[0] + 1 :]
                )

        return s

    def _construct_gamma_line(self, transition, identifiers):

        props = {
            "E_gamma": [9, 19],
            "Delta_E": [19, 21],
            "Relative_Total_Intensity": [21, 29],
            "Relative_Total_Intensity_Uncertainty": [29, 31],
            "Transition_Multipolarity": [31, 41],
            "Mixing_Ratio": [41, 49],
            "Mixing_Ratio_Uncertainty": [49, 55],
            "Total_Conversion_Coefficient": [55, 62],
            "Total_Conversion_Coefficient_Uncertainty": [62, 64],
            "Relative_Total_Transition_Intensity": [64, 74],
            "Relative_Total_Transition_Intensity_Uncertainty": [74, 76],
            "Comment": [76],
            "Coincidence": [77],
            "Question": [79],
        }
        properties = transition.get_properties()

        s = " " * 80

        s = identifiers[1] + s[8:]

        for key, indices in props.items():
            if key in properties and len(indices) == 2:
                s = (
                    s[: indices[0]]
                    + str(properties[key]).center(indices[1] - indices[0])
                    + s[indices[1] :]
                )
            if key in properties and len(indices) == 1:
                s = (
                    s[: indices[0]]
                    + str(properties[key])
                    + s[indices[0] + 1 :]
                )

        return s
