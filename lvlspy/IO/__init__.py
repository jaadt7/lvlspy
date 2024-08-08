"""
A subdirectoy of lvlspy to handle input and output
"""

import os
from lvlspy.IO.xml import *
from lvlspy.IO.ENSDF import *

xml_catalog = os.path.join(os.path.dirname(__file__), "xsd_pub/catalog")

if "XML_CATALOG_FILES" in os.environ:
    os.environ["XML_CATALOG_FILES"] += " " + xml_catalog
else:
    os.environ["XML_CATALOG_FILES"] = xml_catalog
