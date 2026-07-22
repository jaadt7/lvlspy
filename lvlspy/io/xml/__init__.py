"""Compatibility wrapper for :mod:`lvlspy.extensions.io.xml`."""

from lvlspy.extensions.io.xml import (
    XML_CATALOG,
    update_from_xml,
    validate,
    write_to_xml,
)

__all__ = ["XML_CATALOG", "update_from_xml", "validate", "write_to_xml"]
