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

        t = lt.Transition(lvs[tran[1][0]], lvs[tran[1][1]], 0.0)
        t = _set_transition_properties(t, tran[1])
        ein_a = calc.Weisskopf().estimate_from_ensdf(t, a)
        t.update_einstein_a(ein_a)
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
    if t.get_properties()["Reduced_Matrix_Coefficient"] != "":
        _extract_rmc(t)
    return t


def _extract_rmc(t):
    s = t.get_properties()["Reduced_Matrix_Coefficient"]
    parts = s.split("$")
    if len(parts) not in (1, 2):
        raise ValueError(
            "Malformed ENSDF reduced-matrix-coefficient record: " f"{s!r}"
        )

    _extract_rmc_term(parts[0], t, 1)
    if len(parts) == 2:
        _extract_rmc_term(parts[1], t, 2)

    return t


def _extract_rmc_term(term, t, index):
    match = re.search(r"(\S+)\s*([=<>])\s*([^\s$]+)", term)
    if not match:
        raise ValueError(
            "Malformed ENSDF reduced-matrix-coefficient term: "
            f"{term.strip()!r}"
        )

    coefficient_type, operator, coefficient_value = match.groups()
    if operator not in ("=", "<", ">"):
        raise ValueError(
            "Malformed ENSDF reduced-matrix-coefficient operator: "
            f"{operator!r}"
        )

    try:
        coefficient_val = float(coefficient_value)
    except ValueError as exc:
        raise ValueError(
            "Malformed ENSDF reduced-matrix-coefficient value: "
            f"{coefficient_value!r}"
        ) from exc

    t.update_properties({f"tran_{index}_type": coefficient_type})
    t.update_properties({f"tran_{index}_val": coefficient_val})


def update_reduced_matrix_coefficient(sp, a, t, rmc, mr=0):
    """Method to update a transition's reduced matrix coefficient and Einstein A coefficient

    Args:
        ``sp`` (:obj:`lvlspy.species`) The species where the transition is found

        ``a`` (:obj:`int`) The species mass number

        ``t`` (:obj:`lvlspy.transition`) The transition to be updated

        ``rmc`` (:obj:`list`) A list of tuples containing the new updated
                              reduced matrix coefficients. A sample would be
                              [('BM1W',0.05)]

        ``mr`` (:obj:`float`,optional) An updated mixing ratio


    Returns:
        On successful return, the transition's Einstein A coefficient will be
        updated based on the new coefficients.

    """
    s = sp.get_name()
    identifiers = _get_file_sp_and_identifiers(re.search(r"\d+", s), s, a)

    if mr != 0:
        t.update_properties({"Mixing_Ratio": mr})

    for i, b in enumerate(rmc):
        t.update_properties({"tran_" + str(i + 1) + "_type": b[0]})
        t.update_properties({"tran_" + str(i + 1) + "_val": b[1]})

    new_string = identifiers[2] + " G " + rmc[0][0] + "=" + str(rmc[0][1])
    if len(rmc) == 2:
        new_string = new_string + "$" + rmc[1][0] + "=" + str(rmc[1][1])

    t.update_properties({"Reduced_Matrix_Coefficient": new_string})
    t.update_einstein_a(calc.Weisskopf().estimate_from_ensdf(t, a))

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


def _parse_energy_field(field, offset_symbols, default=None):
    """Parse an ENSDF energy after removing symbolic offset notation."""

    energy = field.strip()
    if not energy or energy.isalpha():
        if default is not None:
            return default
        raise ValueError("ENSDF level energy is blank or nonnumeric")

    if len(energy) >= 2 and energy[0] in offset_symbols and energy[1] == "+":
        energy = energy[2:]
    if len(energy) >= 2 and energy[-1] in offset_symbols and energy[-2] == "+":
        energy = energy[:-2]

    if not energy:
        if default is not None:
            return default
        raise ValueError("ENSDF level energy contains only an offset symbol")

    return float(energy)


def _read_levels(line, a, zero_counter):
    energy = _parse_energy_field(line[9:19], a)
    temp = []
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
    energy_field = line[9:19].strip()
    energy_is_known = bool(energy_field) and not energy_field.isalpha()
    e_g = _parse_energy_field(energy_field, a, default=0.0)
    index = -1
    for i, lev in enumerate(lvls[:-1] if energy_is_known else []):

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
    normalized_jpi = jpi.replace("(", "").replace(")", "")

    if normalized_jpi == "":
        multi = 10000
        parity = "+"
        useable = False

    elif (
        "TO" in normalized_jpi
        or "," in normalized_jpi
        or ":" in normalized_jpi
        or "OR" in normalized_jpi
    ):
        useable = False
        j_range = _get_jpi_range(jpi)
        multi = j_range[0][0]
        parity = j_range[0][1]

    else:
        parity = (
            normalized_jpi[-1] if normalized_jpi[-1] in ("+", "-") else None
        )
        spin = normalized_jpi[:-1] if parity is not None else normalized_jpi
        if spin:
            multi = int(2 * lp.Properties().evaluate_expression(spin) + 1)
            useable = parity is not None
            if parity is None:
                parity = "+"
        else:
            multi = 10000
            useable = False

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
                        reduced_matrix_coefficient = (
                            transition.get_properties().get(
                                "Reduced_Matrix_Coefficient"
                            )
                        )
                        if reduced_matrix_coefficient:
                            f.write(
                                str(reduced_matrix_coefficient).rstrip("\n")
                                + "\n"
                            )


def _construct_level_line(lev, identifiers):
    energy = lev.get_energy()
    properties = lev.get_properties()

    props = {
        "energy uncertainty": [19, 21],
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
    s = (
        s[:9]
        + _format_fixed_width_field(energy, 19 - 9, "level energy")
        + s[19:]
    )
    for key, indices in props.items():
        property_key = key
        if (
            key == "energy uncertainty"
            and key not in properties
            and "energy_uncertainty" in properties
        ):
            property_key = "energy_uncertainty"

        if property_key in properties and len(indices) == 2:
            s = (
                s[: indices[0]]
                + _format_fixed_width_field(
                    properties[property_key],
                    indices[1] - indices[0],
                    f"level property {property_key!r}",
                )
                + s[indices[1] :]
            )
        if property_key in properties and len(indices) == 1:
            value = str(properties[property_key])
            if len(value) > 1:
                raise ValueError(
                    "ENSDF level property "
                    f"{property_key!r} does not fit in its 1-character field"
                )
            s = s[: indices[0]] + value + s[indices[0] + 1 :]

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
                + _format_fixed_width_field(
                    properties[key],
                    indices[1] - indices[0],
                    f"gamma property {key!r}",
                )
                + s[indices[1] :]
            )
        if key in properties and len(indices) == 1:
            value = str(properties[key])
            if len(value) > 1:
                raise ValueError(
                    "ENSDF gamma property "
                    f"{key!r} does not fit in its 1-character field"
                )
            s = s[: indices[0]] + str(properties[key]) + s[indices[0] + 1 :]

    return s


def _format_fixed_width_field(value, width, field_name):
    text = str(value)
    if len(text) > width:
        raise ValueError(
            f"ENSDF {field_name} {text!r} does not fit in a {width}-character field"
        )
    return text.center(width)


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
                        calc.spin_from_multiplicity(
                            levels[i].get_multiplicity()
                        ),
                        calc.spin_from_multiplicity(
                            levels[j].get_multiplicity()
                        ),
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
            jj = [
                calc.spin_from_multiplicity(ki[0]),
                calc.spin_from_multiplicity(kj[0]),
            ]
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
        jj = [
            calc.spin_from_multiplicity(in_list[3].get_multiplicity()),
            calc.spin_from_multiplicity(k[0]),
        ]
        p = [in_list[3].get_properties()["parity"], k[1]]
        p = lp.Properties().set_parity(p)
        in_list[1] += calc.Weisskopf().estimate(
            in_list[0], jj, p, in_list[4]
        ) / len(jpi_j_range)

    return in_list[1]


def _get_ein_a_from_mixed_upper_level_to_lower(in_list):

    jpi_i_range = _get_jpi_range(in_list[2])
    for k in jpi_i_range:
        jj = [
            calc.spin_from_multiplicity(k[0]),
            calc.spin_from_multiplicity(in_list[3].get_multiplicity()),
        ]
        p = [k[1], in_list[3].get_properties()["parity"]]
        p = lp.Properties().set_parity(p)
        in_list[1] += calc.Weisskopf().estimate(
            in_list[0], jj, p, in_list[4]
        ) / len(jpi_i_range)
    return in_list[1]


def _get_jpi_range(jpi):
    grouped_alternative_parity = None
    grouped_alternatives = re.fullmatch(r"\((.+)\)([+-])", jpi.strip())
    if grouped_alternatives and (
        "," in grouped_alternatives.group(1)
        or "OR" in grouped_alternatives.group(1)
    ):
        jpi = grouped_alternatives.group(1)
        grouped_alternative_parity = grouped_alternatives.group(2)
    else:
        jpi = jpi.replace("(", "").replace(")", "")
    j_range = []
    if jpi == "":
        return j_range
    if "TO" in jpi or ":" in jpi:
        endpoints = jpi.split("TO") if "TO" in jpi else jpi.split(":")
        return _build_jpi_range_from_endpoints(
            endpoints, grouped_alternative_parity
        )

    return _build_jpi_range_from_assignments(jpi, grouped_alternative_parity)


def _build_jpi_range_from_endpoints(endpoints, grouped_parity):
    """Build an inclusive J range from ENSDF TO or : notation."""

    j_range = []
    m1, p1 = _parse_jpi_endpoint(endpoints[0])
    m2, p2 = _parse_jpi_endpoint(endpoints[1])

    # ENSDF defines J TO J'PI as an inclusive range with parity PI.
    # Since multiplicity is 2J+1, unit steps in J are steps of two here.
    if p1 is None and p2 is not None:
        for multiplicity in range(m1, m2 + 1, 2):
            j_range.append([multiplicity, p2])
        return j_range

    for multiplicity in range(m1, m2 + 1, 2):
        if multiplicity == m1 and p1 is not None:
            parities = [p1]
        elif multiplicity == m2 and p2 is not None:
            parities = [p2]
        elif grouped_parity is not None:
            parities = [grouped_parity]
        else:
            parities = ["+", "-"]
        for parity in parities:
            j_range.append([multiplicity, parity])

    return j_range


def _build_jpi_range_from_assignments(jpi, grouped_parity):
    """Build a J range from ENSDF comma-separated or OR-separated choices."""

    if "OR" in jpi:
        assignments = jpi.split("OR")
    elif "," in jpi:
        assignments = jpi.split(",")
    else:
        assignments = [jpi]

    j_range = []
    for assignment in assignments:
        assignment = assignment.strip()
        if assignment in ("+", "-"):
            continue

        multiplicity, parity = _parse_jpi_endpoint(assignment)
        if parity is None and grouped_parity is not None:
            parity = grouped_parity
        if parity is None:
            j_range.append([multiplicity, "+"])
            j_range.append([multiplicity, "-"])
        else:
            j_range.append([multiplicity, parity])

    return j_range


def _parse_jpi_endpoint(endpoint):
    endpoint = endpoint.strip()
    parity = endpoint[-1] if endpoint[-1] in ("+", "-") else None
    if parity is not None:
        endpoint = endpoint[:-1]
    multiplicity = int(2 * lp.Properties().evaluate_expression(endpoint) + 1)
    return multiplicity, parity


def remove_undefined_levels(sp, all_levs=False):
    """Method that removes levels read from ensdf where j^pi is left blank or unclear.
    This feature Wfacilitates calculations made in the isomer module

    Args:
        ``sp`` (:obj:`lvlspy.species.Species`) The species of which the levels are to be trimmed

        ``all`` (:obj:`bool`) A flag to remove all undefined levels which have j^pi set blank or
        a range of values. Defaults to False so only the blanks are removed

    Returns:
        Upon successful return, the levels with blank j^pi from the ENSDF record will be removed
    """
    levels = sp.get_levels()
    if all_levs:
        for l in levels:
            if l.get_properties()["useability"] is False:
                sp.remove_level(l)
    else:
        for l in levels:
            if l.get_properties()["j^pi"] == "":
                sp.remove_level(l)
