"""Tests for vendored XML schema resources and provenance."""

import io
from importlib.resources import files
from pathlib import Path

from lvlspy.io.xml import validate

EXPECTED_SCHEMA_FILES = {
    "catalog",
    "level_types.xsd",
    "levels.xsd",
    "liblvls_input.xsd",
    "spcoll.xsd",
    "zone_types.xsd",
    "zones.xsd",
    "README.md",
}


def test_all_vendored_schema_resources_are_available():
    schema_directory = files("lvlspy.io.xml") / "xsd_pub"

    for filename in EXPECTED_SCHEMA_FILES:
        assert (schema_directory / filename).is_file(), filename


def test_schema_provenance_matches_recorded_revision():
    repository_root = Path(__file__).parent.parent
    revision = (
        (repository_root / "XSD_REVISION").read_text(encoding="ascii").strip()
    )
    provenance = (
        repository_root / "lvlspy" / "io" / "xml" / "xsd_pub" / "README.md"
    ).read_text(encoding="utf-8")

    assert len(revision) == 40
    assert all(character in "0123456789abcdef" for character in revision)
    assert f"Upstream commit: `{revision}`" in provenance


def test_vendored_schema_validates_without_network_access():
    assert validate(io.BytesIO(b"<species_collection/>")) is None
