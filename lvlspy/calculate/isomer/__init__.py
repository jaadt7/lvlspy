"""
A submodule to handle calculations involving isomers
"""

import os
from . import _isomer

# Auto-generate __all__ from public symbols in _isomer
__all__ = [name for name in dir(_isomer) if not name.startswith("_")]

# Add public names to the module's global namespace
globals().update({name: getattr(_isomer, name) for name in __all__})

# Fix __module__ so Sphinx shows them as lvlspy.io.xml.validate (not _isomer.validate)
for name in __all__:
    obj = getattr(_isomer, name)
    if hasattr(obj, "__module__"):
        obj.__module__ = __name__
