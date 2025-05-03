"""
A submodule to handle input and output of data in ENSDF format.
"""

import os
from . import _ensdf

# Auto-generate __all__ from public symbols in _ensdf
__all__ = [name for name in dir(_ensdf) if not name.startswith("_")]

# Add public names to the module's global namespace
globals().update({name: getattr(_ensdf, name) for name in __all__})
