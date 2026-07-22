"""Tests for quantum levels."""

import pytest

from lvlspy.core.level import Level


@pytest.mark.parametrize(
    ("energy", "units"),
    [
        (1000.0, "eV"),
        (2.0, "keV"),
        (1.5, "MeV"),
        (0.002, "GeV"),
    ],
)
def test_update_energy_uses_requested_units(energy, units):
    """Updating and constructing a level apply the same unit conversion."""

    level = Level(0.0, 1)
    level.update_energy(energy, units=units)

    assert level.get_energy(units=units) == pytest.approx(energy)
    assert level.get_energy() == pytest.approx(
        Level(energy, 1, units=units).get_energy()
    )


def test_zero_temperature_boltzmann_factor_retains_multiplicity():
    """A zero-energy level has its full statistical weight at zero K."""

    assert Level(0.0, 5).compute_boltzmann_factor(0.0) == 5


def test_boltzmann_factor_rejects_negative_temperature():
    """Negative temperatures are rejected by the Boltzmann factor."""

    with pytest.raises(ValueError, match="temperature must be nonnegative"):
        Level(0.0, 1).compute_boltzmann_factor(-1.0)


@pytest.mark.parametrize("multiplicity", [0, -1, 2.5, float("nan")])
def test_level_rejects_invalid_multiplicity(multiplicity):
    """Invalid multiplicities are rejected at construction time."""

    with pytest.raises(ValueError, match="multiplicity must be a finite positive integer"):
        Level(0.0, multiplicity)


def test_update_multiplicity_rejects_invalid_multiplicity():
    """Invalid multiplicities are rejected during updates."""

    level = Level(0.0, 1)

    with pytest.raises(ValueError, match="multiplicity must be a finite positive integer"):
        level.update_multiplicity(0)
