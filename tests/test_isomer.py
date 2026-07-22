"""Tests for isomer calculations."""

import numpy as np
import pytest

from lvlspy.extensions.calculate.isomer import (
    cascade_probabilities,
    effective_rate,
    ensemble_weights,
)
from lvlspy.core.level import Level
from lvlspy.core.species import Species
from lvlspy.core.transition import Transition


class FourLevelSpecies:
    """Controlled four-level system with two independent cascade states."""

    def compute_rate_matrix(self, temperature):
        del temperature
        return np.array(
            [
                [3.0, 1.0, 0.0, 1.0],
                [2.0, 2.0, 1.0, 0.0],
                [0.0, 1.0, 4.0, 1.0],
                [1.0, 0.0, 3.0, 2.0],
            ]
        )

    def compute_equilibrium_probabilities(self, temperature):
        del temperature
        return np.array([0.1, 0.2, 0.3, 0.4])

    def get_levels(self):
        return [Level(0.0, multiplicity) for multiplicity in (1, 3, 5, 7)]


class ThreeLevelSpecies:
    """Controlled system containing direct and one-step cascade paths."""

    def compute_rate_matrix(self, temperature):
        del temperature
        return np.array(
            [
                [-5.0, 5.0, 11.0],
                [2.0, -12.0, 13.0],
                [3.0, 7.0, -24.0],
            ]
        )


class SingularThreeLevelSpecies:
    """Controlled system whose reduced transfer matrix is singular."""

    def compute_rate_matrix(self, temperature):
        del temperature
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 1.0, 0.0],
                [0.0, 1.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )


def test_ensemble_weights_support_arbitrary_reference_levels():
    """Weights and enhancement factors follow the documented return contract."""

    result = ensemble_weights(
        1.0, FourLevelSpecies(), level_low=1, level_high=3
    )
    (
        w_low,
        w_high,
        big_w_low,
        big_w_high,
        r_lowk,
        r_highk,
        g_low,
        g_high,
    ) = result

    expected_w_low = np.array([1.0 / 3.0, 1.0, 3.0 / 8.0, 0.0])
    expected_w_high = np.array([1.0 / 12.0, 0.0, 9.0 / 16.0, 1.0])

    np.testing.assert_allclose(w_low, expected_w_low)
    np.testing.assert_allclose(w_high, expected_w_high)
    np.testing.assert_allclose(r_lowk, [0.5, 1.5])
    np.testing.assert_allclose(r_highk, [0.25, 0.75])
    np.testing.assert_allclose(big_w_low, expected_w_low.sum())
    np.testing.assert_allclose(big_w_high, expected_w_high.sum())
    np.testing.assert_allclose(g_low, 3.0 * expected_w_low.sum())
    np.testing.assert_allclose(g_high, 7.0 * expected_w_high.sum())


def test_effective_rate_includes_direct_transition_without_intermediates():
    """A direct decay remains effective in a two-level system."""

    lower = Level(0.0, 1)
    upper = Level(100.0, 3)
    species = Species(
        "direct", [lower, upper], [Transition(upper, lower, 2.0)]
    )

    low_to_high, high_to_low = effective_rate(0.0, species)

    np.testing.assert_allclose(low_to_high, 0.0)
    np.testing.assert_allclose(high_to_low, 2.0)


def test_effective_rate_adds_direct_and_cascade_paths():
    """Direct rates are added to paths through intermediate levels."""

    low_to_high, high_to_low = effective_rate(1.0, ThreeLevelSpecies())

    np.testing.assert_allclose(low_to_high, 2.0 + 3.0 * 13.0 / 24.0)
    np.testing.assert_allclose(high_to_low, 5.0 + 7.0 * 11.0 / 24.0)


def test_zero_temperature_cascade_has_finite_effective_rates():
    """A ground level with no outgoing rate has zero upward branching."""

    lower = Level(0.0, 1)
    intermediate = Level(100.0, 3)
    upper = Level(200.0, 5)
    species = Species(
        "cascade",
        [lower, intermediate, upper],
        [
            Transition(intermediate, lower, 2.0),
            Transition(upper, intermediate, 3.0),
        ],
    )

    rates = effective_rate(0.0, species, level_low=0, level_high=2)
    cascades = cascade_probabilities(0.0, species, level_low=0, level_high=2)

    np.testing.assert_allclose(rates, [0.0, 3.0])
    assert all(np.all(np.isfinite(values)) for values in cascades)


def test_disconnected_intermediate_level_has_zero_branching():
    """An intermediate level with no outgoing rate does not create NaNs."""

    lower = Level(0.0, 1)
    upper = Level(100.0, 3)
    disconnected = Level(200.0, 5)
    species = Species(
        "disconnected",
        [lower, upper, disconnected],
        [Transition(upper, lower, 2.0)],
    )

    rates = effective_rate(0.0, species)
    cascades = cascade_probabilities(0.0, species)

    np.testing.assert_allclose(rates, [0.0, 2.0])
    assert all(np.all(np.isfinite(values)) for values in cascades)


def test_singular_transfer_system_raises_descriptive_error():
    """Singular reduced systems are reported clearly."""

    with pytest.raises(ValueError, match="Isomer transfer system is singular"):
        effective_rate(0.0, SingularThreeLevelSpecies(), level_low=0, level_high=3)
