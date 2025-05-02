"""
A module to handle input and output of xml.
"""

import os
from . import _xml

# Auto-generate __all__ from public symbols in _xml
__all__ = [name for name in dir(_xml) if not name.startswith("_")]

# Add public names to the module's global namespace
globals().update({name: getattr(_xml, name) for name in __all__})

# Fix __module__ so Sphinx shows them as lvlspy.io.xml.validate (not _xml.validate)
for name in __all__:
    obj = getattr(_xml, name)
    if hasattr(obj, "__module__"):
        obj.__module__ = __name__

xml_catalog = os.path.join(os.path.dirname(__file__), "xsd_pub/catalog")

if "XML_CATALOG_FILES" in os.environ:
    os.environ["XML_CATALOG_FILES"] += " " + xml_catalog
else:
    os.environ["XML_CATALOG_FILES"] = xml_catalog
