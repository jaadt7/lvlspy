"""Tests for transitions between quantum levels."""

import pytest

from lvlspy.level import Level
from lvlspy.transition import Transition


def test_zero_temperature_has_only_spontaneous_decay():
    """The zero-temperature limit contains no induced transitions."""

    einstein_a = 2.5
    transition = Transition(Level(100.0, 3), Level(0.0, 1), einstein_a)

    assert transition._bb(0.0) == 0.0
    assert transition.compute_lower_to_upper_rate(0.0) == 0.0
    assert transition.compute_upper_to_lower_rate(0.0) == einstein_a


@pytest.mark.parametrize(
    ("upper_energy", "lower_energy"), [(100.0, 100.0), (0.0, 100.0)]
)
def test_default_rates_reject_nonpositive_energy_gaps(
    upper_energy, lower_energy
):
    transition = Transition(
        Level(upper_energy, 3), Level(lower_energy, 1), 2.5
    )

    with pytest.raises(
        ValueError, match="upper-level energy greater than lower-level energy"
    ):
        transition.compute_lower_to_upper_rate(1.0e9)
    with pytest.raises(
        ValueError, match="upper-level energy greater than lower-level energy"
    ):
        transition.compute_upper_to_lower_rate(1.0e9)


def test_custom_rates_allow_nonradiative_degenerate_transition():
    """Custom callbacks do not require a positive photon frequency."""

    transition = Transition(Level(100.0, 3), Level(100.0, 1), 2.5)

    assert transition.compute_lower_to_upper_rate(1.0, lambda _t: 4.0) == 4.0
    assert transition.compute_upper_to_lower_rate(1.0, lambda _t: 5.0) == 5.0


def test_default_rates_reject_negative_temperature():
    transition = Transition(Level(100.0, 3), Level(0.0, 1), 2.5)

    with pytest.raises(ValueError, match="temperature must be nonnegative"):
        transition.compute_lower_to_upper_rate(-1.0)
    with pytest.raises(ValueError, match="temperature must be nonnegative"):
        transition.compute_upper_to_lower_rate(-1.0)


def test_custom_rates_control_their_temperature_domain():
    transition = Transition(Level(100.0, 3), Level(0.0, 1), 2.5)

    assert transition.compute_lower_to_upper_rate(-1.0, lambda _t: 4.0) == 4.0
    assert transition.compute_upper_to_lower_rate(-1.0, lambda _t: 5.0) == 5.0


@pytest.mark.parametrize("einstein_a", [-1.0, float("nan")])
def test_transition_rejects_invalid_einstein_a(einstein_a):
    with pytest.raises(ValueError, match="Einstein A coefficient"):
        Transition(Level(100.0, 3), Level(0.0, 1), einstein_a)


def test_transition_update_rejects_invalid_einstein_a():
    transition = Transition(Level(100.0, 3), Level(0.0, 1), 2.5)

    with pytest.raises(ValueError, match="Einstein A coefficient"):
        transition.update_einstein_a(float("inf"))
