"""Tests for ENSDF input handling."""

import pytest

from lvlspy.extensions.io.ensdf._ensdf import (
    _extract_multi_parity,
    _get_jpi_range,
    _read_transition,
    update_from_ensdf,
    write_to_ensdf,
)
from lvlspy.core.level import Level
from lvlspy.core.spcoll import SpColl
from lvlspy.core.species import Species
from lvlspy.core.transition import Transition


def _make_ensdf_collection(reduced_matrix_coefficient=None):
    lower = Level(0.0, 1)
    upper = Level(100.0, 3)
    lower.update_properties({"j^pi": "0+"})
    upper.update_properties({"j^pi": "1+"})

    transition = Transition(upper, lower, 1.0)
    transition.update_properties(
        {"E_gamma": 100.0, "Transition_Multipolarity": "M1"}
    )
    if reduced_matrix_coefficient is not None:
        transition.update_properties(
            {"Reduced_Matrix_Coefficient": reduced_matrix_coefficient}
        )

    return SpColl([Species("Al26", [lower, upper], [transition])])


def _make_gamma_line(energy):
    return " " * 9 + energy.ljust(10) + " " * 61


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 TO 3+", [[3, "+"], [5, "+"], [7, "+"]]),
        ("1 TO 3-", [[3, "-"], [5, "-"], [7, "-"]]),
        ("1/2:5/2+", [[2, "+"], [4, "+"], [6, "+"]]),
        ("1+ TO 3-", [[3, "+"], [5, "+"], [5, "-"], [7, "-"]]),
        ("1+ TO 3", [[3, "+"], [5, "+"], [5, "-"], [7, "+"], [7, "-"]]),
    ],
)
def test_get_jpi_range_follows_ensdf_range_rules(expression, expected):
    """Spin ranges advance by one in J and apply documented parity rules."""

    assert _get_jpi_range(expression) == expected


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("3+", (7, "+", True)),
        ("3", (7, "+", False)),
        ("+", (10000, "+", False)),
        ("-", (10000, "-", False)),
        ("", (10000, "+", False)),
        ("(3+)", (7, "+", True)),
        ("(3)", (7, "+", False)),
    ],
)
def test_extract_multi_parity_distinguishes_incomplete_assignments(
    expression, expected
):
    """A level is usable only when both its spin and parity are known."""

    assert _extract_multi_parity(expression) == expected


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("3", [[7, "+"], [7, "-"]]),
        ("1/2", [[2, "+"], [2, "-"]]),
        ("(3)", [[7, "+"], [7, "-"]]),
        ("+", []),
    ],
)
def test_get_jpi_range_expands_unknown_parity(expression, expected):
    """Known spins with unknown parity contribute both parity candidates."""

    assert _get_jpi_range(expression) == expected


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("(3,4)-", [[7, "-"], [9, "-"]]),
        ("(3,4)+", [[7, "+"], [9, "+"]]),
        ("(1/2,3/2)+", [[2, "+"], [4, "+"]]),
        ("3+ OR 4-", [[7, "+"], [9, "-"]]),
        ("3 OR 4+", [[7, "+"], [7, "-"], [9, "+"]]),
    ],
)
def test_get_jpi_range_applies_grouped_and_individual_parities(
    expression, expected
):
    """A parity outside parentheses applies to the full alternative group."""

    assert _get_jpi_range(expression) == expected


def test_extract_multi_parity_uses_group_parity_for_placeholder():
    """The placeholder for a grouped assignment retains its shared parity."""

    assert _extract_multi_parity("(3,4)-") == (7, "-", False)


def test_ensdf_round_trip_without_reduced_matrix_coefficient(tmp_path):
    """The optional continuation record may be absent."""

    output = tmp_path / "levels.ens"
    write_to_ensdf(_make_ensdf_collection(), output)

    result = SpColl()
    update_from_ensdf(result, output, "Al26")

    transitions = result.get()["Al26"].get_transitions()
    assert len(transitions) == 1
    assert transitions[0].get_properties()["Reduced_Matrix_Coefficient"] == ""


def test_ensdf_round_trip_with_reduced_matrix_coefficient(tmp_path):
    """A supplied continuation record is emitted on its own line and restored."""

    coefficient = " 26ALB  G BM1W=0.05"
    output = tmp_path / "levels.ens"
    write_to_ensdf(_make_ensdf_collection(coefficient), output)

    assert coefficient in output.read_text(encoding="utf-8").splitlines()

    result = SpColl()
    update_from_ensdf(result, output, "Al26")

    transition = result.get()["Al26"].get_transitions()[0]
    assert (
        transition.get_properties()["Reduced_Matrix_Coefficient"].rstrip("\n")
        == coefficient
    )


def test_ensdf_import_rejects_malformed_reduced_matrix_coefficient(tmp_path):
    """Malformed continuation records fail with a descriptive error."""

    output = tmp_path / "levels.ens"
    write_to_ensdf(
        _make_ensdf_collection(" 26ALB  G BM1W=0.05"), output
    )

    lines = output.read_text(encoding="utf-8").splitlines()
    lines[-1] = " 26ALB  G BM1W 0.05"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(
        ValueError, match="Malformed ENSDF reduced-matrix-coefficient"
    ):
        update_from_ensdf(SpColl(), output, "Al26")


def test_ensdf_export_rejects_overlong_level_energy(tmp_path):
    """Level fields must fit the fixed-width ENSDF layout."""

    collection = _make_ensdf_collection()
    collection.get()["Al26"].get_levels()[1].update_energy(12345678901.0)

    with pytest.raises(ValueError, match="level energy"):
        write_to_ensdf(collection, tmp_path / "levels.ens")


def test_ensdf_export_rejects_overlong_gamma_property(tmp_path):
    """Gamma fields must fit the fixed-width ENSDF layout."""

    collection = _make_ensdf_collection()
    transition = collection.get()["Al26"].get_transitions()[0]
    transition.update_properties({"Transition_Multipolarity": "M1M2M3M4M5M"})

    with pytest.raises(ValueError, match="gamma property 'Transition_Multipolarity'"):
        write_to_ensdf(collection, tmp_path / "levels.ens")


@pytest.mark.parametrize(
    ("energy_field", "expected_energy", "expected_lower_index"),
    [
        ("", 0.0, -1),
        ("X", 0.0, -1),
        ("0.0", 0.0, -1),
        ("X+100.0", 100.0, 0),
        ("100.0+X", 100.0, 0),
    ],
)
def test_read_transition_handles_blank_and_offset_gamma_energies(
    energy_field, expected_energy, expected_lower_index
):
    """ENSDF gamma energies accept blank and symbolic offset forms."""

    levels = [[0.0], [100.0]]
    transition = _read_transition(
        _make_gamma_line(energy_field),
        ["X", "Y", "Z", "U", "V", "W", "A", "B"],
        levels,
    )

    assert transition[1] == expected_lower_index
    assert transition[2] == expected_energy


def test_ensdf_import_skips_gamma_without_destination_energy(tmp_path):
    """A blank gamma field cannot create a transition back to its source."""

    collection = _make_ensdf_collection()
    transition = collection.get()["Al26"].get_transitions()[0]
    transition.update_properties({"E_gamma": ""})
    output = tmp_path / "levels.ens"

    write_to_ensdf(collection, output)
    result = SpColl()
    update_from_ensdf(result, output, "Al26")

    assert result.get()["Al26"].get_transitions() == []


@pytest.mark.parametrize(
    "property_name", ["energy uncertainty", "energy_uncertainty"]
)
def test_ensdf_level_energy_uncertainty_round_trip(property_name, tmp_path):
    """Canonical and legacy keys both populate the ENSDF uncertainty field."""

    collection = _make_ensdf_collection()
    collection.get()["Al26"].get_levels()[1].update_properties(
        {property_name: "12"}
    )
    output = tmp_path / "levels.ens"

    write_to_ensdf(collection, output)
    result = SpColl()
    update_from_ensdf(result, output, "Al26")

    imported_upper = result.get()["Al26"].get_levels()[1]
    assert imported_upper.get_properties()["energy uncertainty"] == "12"
