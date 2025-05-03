"""
A submodule to handle calculations involving Weisskopf estimates
"""

import os

from . import _weisskopf

# Auto-generate __all__ from public symbols in _weisskopf
__all__ = [name for name in dir(_weisskopf) if not name.startswith("_")]

# Add public names to the module's global namespace
globals().update({name: getattr(_weisskopf, name) for name in __all__})

from ._weisskopf import *
