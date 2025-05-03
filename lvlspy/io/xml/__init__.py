"""
A module to handle input and output of xml.
"""

import os
from . import _xml

__all__ = [name for name in dir(_xml) if not name.startswith("_")]
globals().update({name: getattr(_xml, name) for name in __all__})

from ._xml import *

xml_catalog = os.path.join(os.path.dirname(__file__), "xsd_pub/catalog")

if "XML_CATALOG_FILES" in os.environ:
    os.environ["XML_CATALOG_FILES"] += " " + xml_catalog
else:
    os.environ["XML_CATALOG_FILES"] = xml_catalog
