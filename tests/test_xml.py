"""Tests for XML input and output."""

import io

import pytest
from lxml import etree

import lvlspy.extensions.io.xml as xml_module
from lvlspy.extensions.io.xml import update_from_xml, write_to_xml
from lvlspy.core.level import Level
from lvlspy.core.spcoll import SpColl
from lvlspy.core.species import Species
from lvlspy.core.transition import Transition


@pytest.fixture
def collection_schema(tmp_path, monkeypatch):
    """Use a minimal local schema to isolate validation behavior."""

    schema_file = tmp_path / "spcoll.xsd"
    schema_file.write_text(
        """\
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="species_collection"/>
</xs:schema>
""",
        encoding="utf-8",
    )
    monkeypatch.setitem(xml_module.validate.__globals__, "_SCHEMA_DIRECTORY", tmp_path)


@pytest.mark.usefixtures("collection_schema")
def test_validate_accepts_schema_compliant_xml():
    """Valid documents retain the existing successful return value."""

    assert xml_module.validate(io.BytesIO(b"<species_collection/>")) is None


@pytest.mark.usefixtures("collection_schema")
def test_validate_rejects_schema_noncompliant_xml():
    """Invalid documents raise with the schema validation details."""

    with pytest.raises(etree.DocumentInvalid):
        xml_module.validate(io.BytesIO(b"<invalid/>"))


def test_update_from_xml_does_not_resolve_external_entities(tmp_path):
    """External entities cannot expose local file contents."""

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("sensitive contents", encoding="utf-8")
    xml_file = io.BytesIO(f"""\
<!DOCTYPE species_collection [
  <!ENTITY secret SYSTEM "{secret_file.as_uri()}">
]>
<species_collection>
  <optional_properties>
    <property name="external">&secret;</property>
  </optional_properties>
</species_collection>
""".encode())

    result = SpColl()
    update_from_xml(result, xml_file)

    assert result.get_properties()["external"] is None
    assert "sensitive contents" not in str(result.get_properties())


def test_update_from_xml_does_not_process_xinclude_by_default(tmp_path):
    """XInclude must be explicitly enabled before local files are read."""

    included_file = tmp_path / "included.xml"
    included_file.write_text(
        '<species name="included"><levels/></species>', encoding="utf-8"
    )
    document = f"""\
<species_collection xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="{included_file.as_uri()}" parse="xml"/>
</species_collection>
""".encode()

    default_result = SpColl()
    update_from_xml(default_result, io.BytesIO(document))
    assert default_result.get() == {}

    included_result = SpColl()
    update_from_xml(included_result, io.BytesIO(document), xinclude=True)
    assert "included" in included_result.get()


def test_xml_round_trip_distinguishes_degenerate_levels():
    """Transition destinations use both level energy and multiplicity."""

    lower = Level(0.0, 1)
    degenerate = Level(0.0, 3)
    upper = Level(10.0, 5)
    species = Species(
        "test",
        levels=[lower, degenerate, upper],
        transitions=[Transition(upper, lower, 7.0)],
    )

    xml_file = io.BytesIO()
    write_to_xml(SpColl([species]), xml_file)
    xml_file.seek(0)

    result = SpColl()
    update_from_xml(result, xml_file)

    transition = result.get()["test"].get_transitions()[0]
    assert transition.get_lower_level().get_energy() == 0.0
    assert transition.get_lower_level().get_multiplicity() == 1


def test_xml_export_uses_current_species_name():
    """Species renames are reflected in XML output."""

    species = Species("old", [Level(0.0, 1), Level(10.0, 3)])
    coll = SpColl([species])
    species.update_name("new")

    xml_file = io.BytesIO()
    write_to_xml(coll, xml_file)
    xml_file.seek(0)

    xml = etree.parse(xml_file)
    assert xml.xpath("string(/species_collection/species/@name)") == "new"


def test_xml_import_resolves_transition_to_later_level():
    """Transition import does not depend on the order of XML levels."""

    xml_file = io.BytesIO(b"""\
<species_collection>
  <species name="test">
    <levels>
      <level>
        <properties><energy>10</energy><multiplicity>3</multiplicity></properties>
        <transitions>
          <transition>
            <to_energy>0</to_energy><to_multiplicity>1</to_multiplicity><a>7</a>
          </transition>
        </transitions>
      </level>
      <level>
        <properties><energy>0</energy><multiplicity>1</multiplicity></properties>
      </level>
    </levels>
  </species>
</species_collection>
""")

    result = SpColl()
    update_from_xml(result, xml_file)

    transition = result.get()["test"].get_transitions()[0]
    assert transition.get_upper_level().get_energy() == 10.0
    assert transition.get_lower_level().get_energy() == 0.0
    assert transition.get_einstein_a() == 7.0


@pytest.mark.parametrize("property_name", ["useability", "useable"])
def test_xml_round_trip_preserves_false_useability(property_name):
    """Boolean usability flags remain false after XML serialization."""

    lower = Level(0.0, 1)
    upper = Level(10.0, 3)
    upper.update_properties({property_name: False})
    species = Species(
        "test",
        [lower, upper],
        [Transition(upper, lower, 7.0)],
    )

    xml_file = io.BytesIO()
    write_to_xml(SpColl([species]), xml_file)
    xml_file.seek(0)
    result = SpColl()
    update_from_xml(result, xml_file)

    imported_species = result.get()["test"]
    imported_upper = imported_species.get_levels()[1]
    assert imported_upper.get_properties()[property_name] is False
    assert not imported_species.compute_rate_matrix(0.0).any()


@pytest.mark.parametrize(
    ("to_energy", "to_multiplicity"), [(5.0, 1), (0.0, 3)]
)
def test_xml_import_rejects_unresolved_transition_destination(
    to_energy, to_multiplicity
):
    """Missing destination energies and multiplicities are reported."""

    xml_file = io.BytesIO(f"""\
<species_collection>
  <species name="test">
    <levels>
      <level>
        <properties><energy>0</energy><multiplicity>1</multiplicity></properties>
      </level>
      <level>
        <properties><energy>10</energy><multiplicity>3</multiplicity></properties>
        <transitions>
          <transition>
            <to_energy>{to_energy}</to_energy>
            <to_multiplicity>{to_multiplicity}</to_multiplicity>
            <a>7</a>
          </transition>
        </transitions>
      </level>
    </levels>
  </species>
</species_collection>
""".encode())

    with pytest.raises(
        ValueError,
        match=(
            r"from level \(10\.0 keV, multiplicity 3\).*"
            rf"\({to_energy} keV, multiplicity {to_multiplicity}\)"
        ),
    ):
        update_from_xml(SpColl(), xml_file)


@pytest.mark.parametrize(
    "property_key",
    [1, ("name",), ("name", "tag1", "tag2", "extra"), ("name", 1)],
)
def test_xml_export_rejects_invalid_property_keys(property_key):
    """Invalid property shapes raise without terminating the process."""

    collection = SpColl()
    collection.update_properties({property_key: "value"})

    with pytest.raises(ValueError, match="XML property"):
        write_to_xml(collection, io.BytesIO())


def test_xml_import_rejects_unsupported_property_attributes():
    xml_file = io.BytesIO(b"""\
<species_collection>
  <optional_properties>
    <property name="rate" tag1="source" tag2="lab" extra="invalid">1</property>
  </optional_properties>
</species_collection>
""")

    with pytest.raises(ValueError, match="only name, tag1, and tag2"):
        update_from_xml(SpColl(), xml_file)
