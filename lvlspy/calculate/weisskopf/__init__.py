"""
A submodule to handle calculations involving Weisskopf estimates
"""

from ._weisskopf import Weisskopf, spin_from_multiplicity

__all__ = [
    "Weisskopf",
    "spin_from_multiplicity",
]
