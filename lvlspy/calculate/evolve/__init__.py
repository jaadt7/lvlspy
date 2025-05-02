"""
A submodule to handle evolution calculations
"""

import os

from . import _evolve

# Auto-generate __all__ from public symbols in _evolve
__all__ = [name for name in dir(_evolve) if not name.startswith("_")]

__all__.remove("csc_matrix")
__all__.remove("expm_multiply")
# Add public names to the module's global namespace
globals().update({name: getattr(_evolve, name) for name in __all__})

# Fix __module__ so Sphinx shows them as lvlspy.io.xml.validate (not _evolve.validate)
for name in __all__:
    obj = getattr(_evolve, name)
    if hasattr(obj, "__module__"):
        obj.__module__ = __name__
