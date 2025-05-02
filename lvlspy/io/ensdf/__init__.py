"""
A submodule to handle input and output of data in ENSDF format.
"""

import os
from . import _ensdf

# Auto-generate __all__ from public symbols in _xml
__all__ = [name for name in dir(_ensdf) if not name.startswith("_")]

# Add public names to the module's global namespace
globals().update({name: getattr(_ensdf, name) for name in __all__})

# Fix __module__ so Sphinx shows them as lvlspy.io.xml.validate (not _xml.validate)
for name in __all__:
    obj = getattr(_ensdf, name)
    if hasattr(obj, "__module__"):
        obj.__module__ = __name__
