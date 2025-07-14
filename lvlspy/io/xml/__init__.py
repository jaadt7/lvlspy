"""
A module to handle input and output of xml.
"""

import os
from . import _fxml

__all__ = [name for name in dir(_fxml) if not name.startswith("_")]
globals().update({name: getattr(_fxml, name) for name in __all__})

xml_catalog = os.path.join(os.path.dirname(__file__), "xsd_pub/catalog")

if "XML_CATALOG_FILES" in os.environ:
    os.environ["XML_CATALOG_FILES"] += " " + xml_catalog
else:
    os.environ["XML_CATALOG_FILES"] = xml_catalog
