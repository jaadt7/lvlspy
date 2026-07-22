"""
A submodule to handle input and output of data in ENSDF format.
"""

from ._ensdf import update_from_ensdf, write_to_ensdf

__all__ = [
    "update_from_ensdf",
    "write_to_ensdf",
]
