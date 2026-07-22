"""Calculation-oriented extensions."""

# pylint: disable=duplicate-code

from lvlspy.extensions.calculate.evolve import csc, newton_raphson
from lvlspy.extensions.calculate.isomer import (
    cascade_probabilities,
    effective_rate,
    ensemble_weights,
)
from lvlspy.extensions.calculate.weisskopf import (
    Weisskopf,
    spin_from_multiplicity,
)

__all__ = [
    "csc",
    "newton_raphson",
    "cascade_probabilities",
    "effective_rate",
    "ensemble_weights",
    "Weisskopf",
    "spin_from_multiplicity",
]
