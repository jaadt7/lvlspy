"""
Module to handle ENSDF input and output
"""

import re
import math

import lvlspy.level as lv
import lvlspy.species as ls
import lvlspy.properties as lp
import lvlspy.transition as lt
import lvlspy.calculate as calc


def update_from_ensdf(coll, file, sp):
    """Method to update a species collection from an ENSDF file.

    Args:
        ``coll`` (:obj:`obj`) The collection to be read from the ENSDF file

        ``file`` (:obj:`str`) The file name to update from.

        ``sp`` (:obj:`str`): The species to be read from file.


    Returns:
        On successful return, the species collection has been updated.

    """

    _get_species_from_ensdf(coll, file, sp)


def _set_level_properties(levels):
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


def _get_species_from_ensdf(coll, file, sp):
    match = re.search(r"\d+", sp)
    a = int(match.group())  # mass number

    identifiers = _get_file_sp_and_identifiers(match, sp, a)

    levels, transitions = _get_level_and_transition_data(file, identifiers)

    # setting the levels and transitions in lvlspy format
    levs = _set_level_properties(levels)
    s = ls.Species(sp, levels=levs)

    lvs = s.get_levels()

    for tran in enumerate(transitions):
        if tran[1][1] == -1:
            continue

        if (
            lvs[tran[1][1]].get_properties()["useability"] is False
            or lvs[tran[1][0]].get_properties()["useability"] is False
        ):
            continue

        ein_a = calc.Weisskopf().estimate_from_ensdf(lvs, tran[1], a)
        t = lt.Transition(lvs[tran[1][0]], lvs[tran[1][1]], ein_a)
        t = _set_transition_properties(t, tran[1])
        s.add_transition(t)

    coll.add_species(s)


def _set_transition_properties(t, tran):
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
    add_properties.append({properties[-1]: tran[-1]})
    for j in add_properties:
        t.update_properties(j)
    return t


def _get_additional_level_properties(line):
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


def _get_additional_gamma_properties(line):
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


def _read_levels(line, a, zero_counter):
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

    properties = _get_additional_level_properties(line)
    multi, parity, useable = _extract_multi_parity(properties[1])

    temp = [
        energy,
        multi,
        parity,
    ]  # temporary dummy array for re-use
    for prop in enumerate(properties):
        temp.append(prop[1])
    temp.append(useable)

    return temp, zero_counter


def _read_transition(line, a, lvls):
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
    properties = _get_additional_gamma_properties(line)
    for prop in enumerate(properties):
        temp.append(prop[1])
    temp.append("")
    return temp


def _get_level_and_transition_data(file, identifiers):

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
                temp, zero_counter = _read_levels(line, a, zero_counter)
                lvls.append(temp)

            if zero_counter == 2:
                lvls.pop(-1)
                break

            # reading in gamma info

            if line.startswith(identifiers[1]):
                temp = _read_transition(line, a, lvls)
                trans.append(temp)

            if line.startswith(identifiers[2]):
                trans[-1][-1] = line

    return lvls, trans


def _extract_multi_parity(jpi):
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
            multi = int(2 * lp.Properties().evaluate_expression(jpi) + 1)
            useable = True
        else:
            parity = jpi[-1]
            multi = int(2 * lp.Properties().evaluate_expression(jpi[0:-1]) + 1)
            useable = True

    return multi, parity, useable


def _get_file_sp_and_identifiers(match, sp, a):

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


def write_to_ensdf(coll, file):
    """
    Method that writes a collection of species to ENSDF format

    Args:
        ``coll`` (:obj:`lvlspy.spcoll.SpColl`) The collection to be written to file.
        Each species in the collection must have the species' name, level and gamma
        properties must be within ENSDF spec

    Returns:
        On successful return, the species collection has been written
    """
    with open(file, "w+", encoding="utf-8") as f:
        for sp in coll.get():

            match = re.search(r"\d+", sp)
            a = int(match.group())  # mass number
            identifiers = _get_file_sp_and_identifiers(match, sp, a)
            levels = coll.get()[sp].get_levels()
            for lev in levels:
                line = _construct_level_line(lev, identifiers)
                f.write(line + "\n")
                linked_levels = coll.get()[sp].get_lower_linked_levels(lev)
                if linked_levels != []:
                    for l_lev in linked_levels:
                        transition = coll.get()[
                            sp
                        ].get_level_to_level_transition(lev, l_lev)
                        line = _construct_gamma_line(transition, identifiers)
                        f.write(line + "\n")
                        if (
                            transition.get_properties()[
                                "Reduced_Matrix_Coefficient"
                            ]
                            != ""
                        ):
                            f.write(
                                transition.get_properties()[
                                    "Reduced_Matrix_Coefficient"
                                ]
                            )


def _construct_level_line(lev, identifiers):
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
            s = s[: indices[0]] + str(properties[key]) + s[indices[0] + 1 :]

    return s


def _construct_gamma_line(transition, identifiers):

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
            s = s[: indices[0]] + str(properties[key]) + s[indices[0] + 1 :]

    return s


def fill_missing_ensdf_transitions(sp, a):
    """Method to fill in missing transitions from either not listed in ENSDF
    or level with useable property flagged as false due to unclear J^pi

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`) The species read in from ENSDF to
        fill in missing transitions

        ``a`` (:obj:`int`) Mass number of species



    Returns:
        Upon successful return, the species would be updated with all transitions
    """

    levels = sp.get_levels()
    for i in range(1, len(levels)):
        for j in range(i):
            if sp.get_level_to_level_transition(levels[i], levels[j]) is None:
                ein_a = 0.0

                jpi_i = levels[i].get_properties()["j^pi"]
                jpi_j = levels[j].get_properties()["j^pi"]

                e = [levels[i].get_energy(), levels[j].get_energy()]

                # if jpi_i == "" or jpi_j == "":

                #    sp.add_transition(
                #        lt.Transition(levels[i], levels[j], ein_a)
                #    )
                #    continue

                if (
                    levels[i].get_properties()["useability"] is False
                    and levels[j].get_properties()["useability"] is True
                ):

                    sp.add_transition(
                        lt.Transition(
                            levels[i],
                            levels[j],
                            _get_ein_a_from_mixed_upper_level_to_lower(
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
                    p = lp.Properties().set_parity(p)
                    sp.add_transition(
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

                    sp.add_transition(
                        lt.Transition(
                            levels[i],
                            levels[j],
                            _get_ein_a_to_mixed_lower_level(
                                [e, ein_a, jpi_j, levels[i], a]
                            ),
                        )
                    )
                    continue

                if (
                    levels[i].get_properties()["useability"] is False
                    and levels[j].get_properties()["useability"] is False
                ):

                    sp.add_transition(
                        lt.Transition(
                            levels[i],
                            levels[j],
                            _get_ein_a_from_mixed_to_mixed(
                                [e, ein_a, jpi_i, jpi_j, a]
                            ),
                        )
                    )
                    continue


def _get_ein_a_from_mixed_to_mixed(in_list):
    jpi_i_range = _get_jpi_range(in_list[2])
    jpi_j_range = _get_jpi_range(in_list[3])
    for ki in jpi_i_range:
        for kj in jpi_j_range:
            jj = [int(ki[0]), int(kj[0])]
            p = [ki[1], kj[1]]
            p = lp.Properties().set_parity(p)
            in_list[1] += (
                calc.Weisskopf().estimate(in_list[0], jj, p, in_list[4])
                / len(jpi_i_range)
                / len(jpi_j_range)
            )

    return in_list[1]


def _get_ein_a_to_mixed_lower_level(in_list):

    jpi_j_range = _get_jpi_range(in_list[2])

    for k in jpi_j_range:
        jj = [int((in_list[3].get_multiplicity() - 1) / 2), int(k[0])]
        p = [in_list[3].get_properties()["parity"], k[1]]
        p = lp.Properties().set_parity(p)
        in_list[1] += calc.Weisskopf().estimate(
            in_list[0], jj, p, in_list[4]
        ) / len(jpi_j_range)

    return in_list[1]


def _get_ein_a_from_mixed_upper_level_to_lower(in_list):

    jpi_i_range = _get_jpi_range(in_list[2])
    for k in jpi_i_range:
        jj = [int(k[0]), int((in_list[3].get_multiplicity() - 1) / 2)]
        p = [k[1], in_list[3].get_properties()["parity"]]
        p = lp.Properties().set_parity(p)
        in_list[1] += calc.Weisskopf().estimate(
            in_list[0], jj, p, in_list[4]
        ) / len(jpi_i_range)
    return in_list[1]


def _get_jpi_range(jpi):

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
                m = int(2 * lp.Properties().evaluate_expression(j[0:-1]) + 1)
                j_range.append([m, p])
    return j_range


def remove_undefined_levels(sp):
    """Method that removes levels read from ensdf where j^pi is left blank. This feature
    facilitates calculations made in the isomer module

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`) The species of which the levels are to be trimmed

    Returns:
        Upon successful return, the levels with blank j^pi from the ENSDF record will be removed
    """
    levels = sp.get_levels()
    for l in levels:
        if l.get_properties()["j^pi"] == "":
            sp.remove_level(l)
