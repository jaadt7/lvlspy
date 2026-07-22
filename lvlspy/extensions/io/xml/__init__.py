"""XML import/export support."""

from pathlib import Path

from ._xml import update_from_xml, validate, write_to_xml

XML_CATALOG = str(Path(__file__).parent / "xsd_pub" / "catalog")

__all__ = ["XML_CATALOG", "update_from_xml", "validate", "write_to_xml"]
