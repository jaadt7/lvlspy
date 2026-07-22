"""Tests for Weisskopf transition estimates."""

import numpy as np
import pytest

from lvlspy.calculate import fill_missing_transitions
from lvlspy.extensions.calculate.weisskopf import (
    Weisskopf,
    spin_from_multiplicity,
)
from lvlspy.extensions.io.ensdf._ensdf import (
    _get_ein_a_from_mixed_upper_level_to_lower,
)
from lvlspy.core.level import Level
from lvlspy.core.species import Species


@pytest.mark.parametrize(
    ("multiplicity", "expected_spin"),
    [(1, 0.0), (2, 0.5), (3, 1.0), (4, 1.5)],
)
def test_spin_from_multiplicity_preserves_half_integer_values(
    multiplicity, expected_spin
):
    """Multiplicity maps directly to the expected half-integer spin."""

    assert spin_from_multiplicity(multiplicity) == expected_spin


def test_estimate_includes_all_multipoles_for_half_integer_spins(monkeypatch):
    """J=3/2 to J=1/2 permits both dipole and quadrupole radiation."""

    weisskopf = Weisskopf()
    calls = []

    def capture_rate_elec(_self, _e_i, _e_f, jj, _a):
        calls.append(("E", jj))
        return 100.0 * jj

    def capture_rate_mag(_self, _e_i, _e_f, jj, _a):
        calls.append(("M", jj))
        return 1000.0 * jj

    monkeypatch.setattr(Weisskopf, "rate_elec", capture_rate_elec)
    monkeypatch.setattr(Weisskopf, "rate_mag", capture_rate_mag)

    result = weisskopf.estimate([100.0, 0.0], [1.5, 0.5], [1, 1], 3)

    assert calls == [("M", 1), ("E", 2)]
    np.testing.assert_allclose(result, 120.0)


def test_fill_missing_transitions_passes_half_integer_spins(monkeypatch):
    """Missing ENSDF transitions preserve the half-integer spin mapping."""

    captured_spins = []

    def capture_estimate(_self, _energies, spins, _parities, _mass):
        captured_spins.append(spins)
        return 1.0

    monkeypatch.setattr(Weisskopf, "estimate", capture_estimate)
    lower = Level(0.0, 2)
    upper = Level(100.0, 4)
    lower.update_properties({"parity": "+"})
    upper.update_properties({"parity": "+"})

    fill_missing_transitions(Species("odd-mass", [lower, upper]), 3)

    assert captured_spins == [[1.5, 0.5]]


def test_ambiguous_ensdf_estimate_passes_half_integer_spins(monkeypatch):
    """Ambiguous ENSDF assignments probe each allowed spin combination."""

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
