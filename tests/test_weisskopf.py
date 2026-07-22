"""Tests for Weisskopf transition estimates."""

import numpy as np
import pytest

from lvlspy.calculate.weisskopf import Weisskopf, spin_from_multiplicity
from lvlspy.io.ensdf._ensdf import (
    _get_ein_a_from_mixed_upper_level_to_lower,
)
from lvlspy.level import Level
from lvlspy.species import Species


@pytest.mark.parametrize(
    ("multiplicity", "expected_spin"),
    [(1, 0.0), (2, 0.5), (3, 1.0), (4, 1.5)],
)
def test_spin_from_multiplicity_preserves_half_integer_values(
    multiplicity, expected_spin
):
    assert spin_from_multiplicity(multiplicity) == expected_spin


def test_estimate_includes_all_multipoles_for_half_integer_spins():
    """J=3/2 to J=1/2 permits both dipole and quadrupole radiation."""

    weisskopf = Weisskopf()
    energies = [100.0, 0.0]
    spins = [1.5, 0.5]
    parities = [1, 1]

    result = weisskopf.estimate(energies, spins, parities, 3)
    expected = weisskopf._get_rate(
        1, parities, energies, 3
    ) + weisskopf._get_rate(2, parities, energies, 3)

    np.testing.assert_allclose(result, expected)


def test_species_fill_missing_transitions_passes_half_integer_spins(
    monkeypatch,
):
    captured_spins = []

    def capture_estimate(_self, _energies, spins, _parities, _mass):
        captured_spins.append(spins)
        return 1.0

    monkeypatch.setattr(Weisskopf, "estimate", capture_estimate)
    lower = Level(0.0, 2)
    upper = Level(100.0, 4)
    lower.update_properties({"parity": "+"})
    upper.update_properties({"parity": "+"})

    Species("odd-mass", [lower, upper]).fill_missing_transitions(3)

    assert captured_spins == [[1.5, 0.5]]


def test_ambiguous_ensdf_estimate_passes_half_integer_spins(monkeypatch):
    captured_spins = []

    def capture_estimate(_self, _energies, spins, _parities, _mass):
        captured_spins.append(spins)
        return 1.0

    monkeypatch.setattr(Weisskopf, "estimate", capture_estimate)
    lower = Level(0.0, 2)
    lower.update_properties({"parity": "+"})

    _get_ein_a_from_mixed_upper_level_to_lower(
        [[100.0, 0.0], 0.0, "1/2 OR 3/2+", lower, 3]
    )

    assert captured_spins == [[0.5, 0.5], [0.5, 0.5], [1.5, 0.5]]
