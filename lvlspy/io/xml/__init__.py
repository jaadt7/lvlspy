"""
A module to handle input and output of xml.
"""

from pathlib import Path

from ._xml import update_from_xml, validate, write_to_xml

XML_CATALOG = str(Path(__file__).parent / "xsd_pub" / "catalog")

__all__ = [
    "update_from_xml",
    "validate",
    "write_to_xml",
]
