"""Tests for species and their rate matrices."""

import numpy as np
import pytest

from lvlspy.core.level import Level
from lvlspy.core.spcoll import SpColl
from lvlspy.core.species import Species
from lvlspy.core.transition import Transition


def make_two_level_species():
    """Return a species containing one downward transition."""

    lower = Level(0.0, 1)
    upper = Level(100.0, 3)
    transition = Transition(upper, lower, 2.5)
    return Species("test", [lower, upper], [transition]), lower, upper


@pytest.mark.parametrize("property_name", ["useability", "useable"])
@pytest.mark.parametrize("property_value", [False, "False", "false"])
def test_rate_matrix_excludes_unuseable_levels(property_name, property_value):
    """ENSDF and legacy flags both exclude connected transitions."""

    species, _, upper = make_two_level_species()
    upper.update_properties({property_name: property_value})

    np.testing.assert_array_equal(species.compute_rate_matrix(1.0e9), 0.0)


def test_rate_matrix_conserves_total_population():
    """Every rate-matrix column sums to zero."""

    species, _, _ = make_two_level_species()
    rate_matrix = species.compute_rate_matrix(1.0e9)

    np.testing.assert_allclose(rate_matrix.sum(axis=0), 0.0)


def test_equilibrium_probabilities_are_invariant_to_energy_offset():
    """Only excitation energies affect normalized Boltzmann weights."""

    base = Species("base", [Level(0.0, 1), Level(100.0, 3)])
    shifted = Species("shifted", [Level(1000.0, 1), Level(1100.0, 3)])

    np.testing.assert_allclose(
        base.compute_equilibrium_probabilities(1.0e9),
        shifted.compute_equilibrium_probabilities(1.0e9),
    )


def test_zero_temperature_weights_degenerate_ground_levels_by_multiplicity():
    """Zero-temperature weights split degenerate ground states by weight."""

    species = Species(
        "degenerate",
        [Level(100.0, 1), Level(100.0, 3), Level(200.0, 5)],
    )

    np.testing.assert_allclose(
        species.compute_equilibrium_probabilities(0.0), [0.25, 0.75, 0.0]
    )


def test_low_temperature_probabilities_do_not_underflow_to_nan():
    """Low temperatures remain finite after normalization."""

    species = Species("shifted", [Level(1000.0, 1), Level(1001.0, 3)])

    probabilities = species.compute_equilibrium_probabilities(1.0)

    np.testing.assert_allclose(probabilities, [1.0, 0.0])
    assert np.all(np.isfinite(probabilities))


def test_species_collection_tracks_renamed_species():
    """Collection lookups track species renames and removals."""

    lower = Level(0.0, 1)
    upper = Level(100.0, 3)
    species = Species("old", [lower, upper])

    coll = SpColl([species])
    species.update_name("new")

    assert "new" in coll.get()
    assert "old" not in coll.get()

    coll.remove_species(species)
    assert not coll.get()
