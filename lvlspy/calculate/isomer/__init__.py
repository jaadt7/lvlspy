"""Compatibility wrapper for :mod:`lvlspy.extensions.calculate.isomer`."""

from lvlspy.extensions.calculate.isomer import (
    cascade_probabilities,
    effective_rate,
    ensemble_weights,
)

__all__ = ["cascade_probabilities", "effective_rate", "ensemble_weights"]
