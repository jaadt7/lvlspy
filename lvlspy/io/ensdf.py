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

    def update_from_ensdf(self, coll, file, sp_list):
        """Method to update a species collection from an ENSDF file.

        Args:
            ``coll`` (:obj: `obj') The collection to be read from the ENSDF file

            ``file`` (:obj: `str`) The name of the XML file from which to update.

            ``sp_list`` (:obj: `list`, optional): List of species to be read from file.
              Defaults to all species.

        Returns:
            On successful return, the species collection has been updated.

        """

        for sp in sp_list:
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
        for l in enumerate(levels):  # setting the level with properties
            levs.append(lv.Level(l[1][0], l[1][1]))
            additional_properties = [
                {key, value} for key, value in zip(properties, l[1][2:-1])
            ]
            for j in additional_properties:
                levs[j].update_properties(j)

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

            ein_a = calc.Weisskopf().estimate_from_ensdf(lvs, tran[1], a)
            t = lt.Transition(lvs[tran[1][0]], lvs[tran[1][1]], ein_a)
            s.add_transition(t)

        coll.add_species(s)

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
                    energy = line[9:19].strip()
                    if energy[0] in a:
                        str_dummy = energy[0] + "+"
                        energy = energy.replace(str_dummy, "")
                    if energy[-1] in a:
                        str_dummy = "+" + energy[-1]
                        energy = energy.replace(str_dummy, "")

                    energy = float(
                        energy
                    )  # strip the spaces and cast to float
                    if energy == 0.0:
                        zero_counter += 1
                    if zero_counter == 2:
                        break  # do not continue reading forward

                    properties = self._get_additional_level_properties(line)
                    multi, parity, useable = self._extract_multi_parity(
                        properties[1]
                    )

                    temp = [
                        energy,
                        multi,
                        parity,
                    ]  # temporary dummy array for re-use
                    for i in range(len(properties)):
                        temp.append(properties[i])
                    temp.append(useable)

                    lvls.append(temp)

                # reading in gamma info

                if line.startswith(identifiers[1]):

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

                    for i in range(len(lvls)):
                        if math.isclose(
                            abs(e_g - (lvls[-1][0] - lvls[i][0])),
                            0.0,
                            abs_tol=1.0,
                        ):
                            index = i
                            break

                    temp = [len(lvls) - 1, index, e_g]
                    properties = self._get_additional_gamma_properties(line)
                    for i in range(len(properties)):
                        temp.append(properties[i])
                    temp.append("")
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
                multi = int(2 * eval(jpi) + 1)
                useable = True
            else:
                parity = jpi[-1]
                multi = int(2 * eval(jpi[0:-1]) + 1)
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
        )  # reduces transition probability identifier

        return [l_identifier, g_identifier, b_identifier]

    def write_to_ensdf(self):
        """
        Method that writes a collection of species to ENSDF format
        """
        return
