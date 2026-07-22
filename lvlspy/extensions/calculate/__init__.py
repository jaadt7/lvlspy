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
from lvlspy.core.transition import Transition


def normalize_parity_pair(parities):
    """Convert a pair of ``+``/``-`` parity values to integers."""

    result = []
    for parity in parities:
        if parity == "+":
            result.append(1)
        else:
            result.append(-1)
    return result


def fill_missing_transitions(sp, a):
    """Fill in missing transitions using Weisskopf estimates."""

    levels = sp.get_levels()
    for i in range(1, len(levels)):
        for j in range(i):
            if (
                sp.get_level_to_level_transition(levels[i], levels[j])
                is not None
            ):
                continue

            energies = [levels[i].get_energy(), levels[j].get_energy()]
            spins = [
                spin_from_multiplicity(levels[i].get_multiplicity()),
                spin_from_multiplicity(levels[j].get_multiplicity()),
            ]
            parities = normalize_parity_pair(
                [
                    levels[i].get_properties()["parity"],
                    levels[j].get_properties()["parity"],
                ]
            )
            ein_a = Weisskopf().estimate(energies, spins, parities, a)
            sp.add_transition(Transition(levels[i], levels[j], ein_a))


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
