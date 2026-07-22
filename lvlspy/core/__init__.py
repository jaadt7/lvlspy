"""Core domain model for lvlspy."""

# pylint: disable=duplicate-code

from lvlspy.core.level import Level
from lvlspy.core.properties import Properties
from lvlspy.core.spcoll import SpColl
from lvlspy.core.species import Species
from lvlspy.core.transition import Transition

__all__ = [
    "Level",
    "Properties",
    "SpColl",
    "Species",
    "Transition",
]
