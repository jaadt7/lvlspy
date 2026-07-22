"""Compatibility wrapper for :mod:`lvlspy.extensions.calculate`."""

# pylint: disable=duplicate-code

from lvlspy.extensions.calculate import (
    Weisskopf,
    cascade_probabilities,
    csc,
    effective_rate,
    ensemble_weights,
    fill_missing_transitions,
    newton_raphson,
    spin_from_multiplicity,
)

__all__ = [
    "csc",
    "newton_raphson",
    "cascade_probabilities",
    "effective_rate",
    "ensemble_weights",
    "fill_missing_transitions",
    "Weisskopf",
    "spin_from_multiplicity",
]
