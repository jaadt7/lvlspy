"""
A package of python routines to handle quantum-level system data.
"""

import os
from lvlspy.spcoll import *
from lvlspy.species import *
from lvlspy.level import *
from lvlspy.transition import *

xml_catalog = os.path.join(os.path.dirname(__file__), "xsd_pub/catalog")

if "XML_CATALOG_FILES" in os.environ:
    os.environ["XML_CATALOG_FILES"] += " " + xml_catalog
else:
    os.environ["XML_CATALOG_FILES"] = xml_catalog
