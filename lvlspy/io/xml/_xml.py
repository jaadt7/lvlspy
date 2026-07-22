"""Module to handle XML input and output"""

from pathlib import Path
from urllib.parse import urlparse

from lxml import etree
import lvlspy.level as lv
import lvlspy.species as ls
import lvlspy.transition as lt

_SCHEMA_DIRECTORY = Path(__file__).parent / "xsd_pub"
_LOCAL_SCHEMA_FILES = frozenset(
    {
        "level_types.xsd",
        "levels.xsd",
        "liblvls_input.xsd",
        "spcoll.xsd",
        "zone_types.xsd",
        "zones.xsd",
    }
)


class _LocalSchemaResolver(etree.Resolver):
    def resolve(self, url, _public_id, context):
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name
        if parsed_url.scheme in ("http", "https") and (
            filename in _LOCAL_SCHEMA_FILES
        ):
            return self.resolve_filename(
                str(_SCHEMA_DIRECTORY / filename), context
            )

        return None


def write_to_xml(coll, file, pretty_print=True, units="keV"):
    """Method to write the collection to XML.

    Args:
        ``coll`` (:obj: `obj') The collection to be written to the XML file
        ``file`` (:obj:`str`) The output file name.

        ``pretty_print`` (:obj:`bool`, optional): If set to True,
        routine outputs the xml in nice indented format.

        ``units`` (:obj:`str`, optional): A string for the energy units.

    Return:
        On successful return, the species collection data have been
        written to the XML output file.

    """

    root = etree.Element("species_collection")
    xml = etree.ElementTree(root)

    _add_optional_properties(root, coll)

    for species_name, species in coll.get().items():
        my_species = etree.SubElement(root, "species", name=species_name)

        _add_optional_properties(my_species, species)

        xml_levels = etree.SubElement(my_species, "levels")

        for level in species.get_levels():
            _add_level_to_xml(xml_levels, species, level, units)

    xml.write(file, pretty_print=pretty_print)


def _add_level_to_xml(xml_levels, species, level, units):
    result = etree.SubElement(xml_levels, "level")
    _add_optional_properties(result, level)
    result_props = etree.SubElement(result, "properties")
    if units != "keV":
        my_energy = etree.SubElement(result_props, "energy", units=units)
    else:
        my_energy = etree.SubElement(result_props, "energy")
    my_energy.text = _get_energy_text(level.get_energy(), units)
    my_multiplicity = etree.SubElement(result_props, "multiplicity")
    my_multiplicity.text = str(level.get_multiplicity())

    _add_transitions_to_xml(result, species, level, units)

    return result


def _add_transitions_to_xml(xml_level, species, level, units):
    lower_levels = species.get_lower_linked_levels(level)

    if len(lower_levels) == 0:
        return

    xml_transitions = etree.SubElement(xml_level, "transitions")

    for lower_level in lower_levels:
        transition = species.get_level_to_level_transition(level, lower_level)
        xml_trans = etree.SubElement(xml_transitions, "transition")
        _add_optional_properties(xml_trans, transition)
        if units != "keV":
            xml_to_energy = etree.SubElement(
                xml_trans, "to_energy", units=units
            )
        else:
            xml_to_energy = etree.SubElement(xml_trans, "to_energy")
        xml_to_energy.text = _get_energy_text(lower_level.get_energy(), units)
        xml_to_multiplicity = etree.SubElement(xml_trans, "to_multiplicity")
        xml_to_multiplicity.text = str(lower_level.get_multiplicity())
        xml_a = etree.SubElement(xml_trans, "a")
        xml_a.text = str(transition.get_einstein_a())


def _add_optional_properties(my_element, my_object):
    my_props = my_object.get_properties()

    if len(my_props):
        props = etree.SubElement(my_element, "optional_properties")
        for prop in my_props:
            if isinstance(prop, str):
                my_prop = etree.SubElement(props, "property", name=prop)
            elif isinstance(prop, tuple):
                if len(prop) not in (2, 3) or not all(
                    isinstance(part, str) for part in prop
                ):
                    raise ValueError(
                        "XML property tuple keys must contain two or three "
                        f"strings: {prop!r}"
                    )
                if len(prop) == 2:
                    my_prop = etree.SubElement(
                        props, "property", name=prop[0], tag1=prop[1]
                    )
                else:
                    my_prop = etree.SubElement(
                        props,
                        "property",
                        name=prop[0],
                        tag1=prop[1],
                        tag2=prop[2],
                    )
            else:
                raise ValueError(
                    "XML property keys must be strings or tuples of strings: "
                    f"{prop!r}"
                )

            my_prop.text = str(my_props[prop])


def validate(file, xinclude=False):
    """Method to validate a species collection XML file.

    Args:
        ``file`` (:obj:`str`) The name of the XML file to validate.

        ``xinclude`` (:obj:`bool`, optional): Process XInclude directives when
        True. Defaults to False.

    Returns:
        Nothing if the document is valid.

    Raises:
        :obj:`lxml.etree.DocumentInvalid`: If the document does not conform to
        the species collection schema.

    """

    xml = _parse_xml(file, xinclude=xinclude)

    schema_parser = etree.XMLParser(resolve_entities=False, no_network=True)
    schema_parser.resolvers.add(  # pylint: disable=no-member
        _LocalSchemaResolver()
    )
    schema_file = _SCHEMA_DIRECTORY / "spcoll.xsd"
    xmlschema_doc = etree.parse(str(schema_file), schema_parser)

    xml_validator = etree.XMLSchema(xmlschema_doc)
    xml_validator.assertValid(xml)


def update_from_xml(coll, file, xpath="", xinclude=False):
    """Method to update a species collection from an XML file.

    Args:
        ``coll`` (:obj:`obj`) The collection to be read from the XML file

        ``file`` (:obj:`str`) The name of the XML file from which to update.

        ``xpath`` (:obj:`str`, optional): XPath expression to select
        species.  Defaults to all species.

        ``xinclude`` (:obj:`bool`, optional): Process XInclude directives when
        True. Defaults to False.

    Returns:
        On successful return, the species collection has been updated.

    """

    xml = _parse_xml(file, xinclude=xinclude)

    spcoll = xml.getroot()

    _update_optional_properties(spcoll, coll)

    for xml_species in spcoll.xpath("//species" + xpath):
        coll.add_species(_get_species_from_xml(xml_species))


def _parse_xml(file, xinclude=False):
    parser = etree.XMLParser(
        remove_blank_text=True,
        resolve_entities=False,
        no_network=True,
    )
    xml = etree.parse(file, parser)
    if xinclude:
        xml.xinclude()
    return xml


def _get_species_from_xml(xml_species):
    level_dict = {}
    result = ls.Species(xml_species.attrib["name"])
    _update_optional_properties(xml_species, result)

    xml_levels = []
    for xml_level in xml_species.xpath(".//level"):
        new_level = _get_level_from_xml(xml_level)
        result.add_level(new_level)
        level_key = (new_level.get_energy(), new_level.get_multiplicity())
        level_dict[level_key] = new_level
        xml_levels.append((xml_level, new_level))

    for xml_level, new_level in xml_levels:
        for xml_trans in xml_level.xpath(".//transition"):
            trans = _get_transition_from_xml(xml_trans, new_level, level_dict)
            result.add_transition(trans)

    return result


def _get_level_from_xml(xml_level):
    props = xml_level.xpath(".//properties")
    energy = props[0].xpath(".//energy")
    multiplicity = props[0].xpath(".//multiplicity")
    attributes = energy[0].attrib
    if "units" in attributes:
        result = lv.Level(
            float(energy[0].text),
            int(multiplicity[0].text),
            units=attributes["units"],
        )
    else:
        result = lv.Level(float(energy[0].text), int(multiplicity[0].text))
    _update_optional_properties(xml_level, result)

    return result


def _get_transition_from_xml(xml_trans, upper_level, level_dict):
    to_energy = xml_trans.xpath(".//to_energy")
    to_multiplicity = xml_trans.xpath(".//to_multiplicity")
    to_a = xml_trans.xpath(".//a")

    f_to_energy = _convert_to_kev(to_energy)
    level_key = (f_to_energy, int(to_multiplicity[0].text))
    if level_key in level_dict:
        result = lt.Transition(
            upper_level,
            level_dict[level_key],
            float(to_a[0].text),
        )
        _update_optional_properties(xml_trans, result)
        return result

    raise ValueError(
        "XML transition from level "
        f"({upper_level.get_energy()} keV, multiplicity "
        f"{upper_level.get_multiplicity()}) references missing destination "
        f"({f_to_energy} keV, multiplicity {level_key[1]})"
    )


def _convert_to_kev(energy):
    attributes = energy[0].attrib
    result = float(energy[0].text)
    if "units" in attributes:
        result /= lv.units_dict[attributes["units"]]
    return result


def _get_energy_text(energy, units):
    return str(energy * lv.units_dict[units])


def _update_optional_properties(my_element, my_object):
    opt_props = my_element.xpath("optional_properties")

    if len(opt_props) > 0:
        props = opt_props[0].xpath("property")

        my_props = {}
        for prop in props:
            attributes = prop.attrib
            my_keys = attributes.keys()
            value = _get_optional_property_value(
                attributes.get("name"), prop.text
            )
            if len(my_keys) == 1:
                my_props[attributes[my_keys[0]]] = value
            elif len(my_keys) == 2:
                my_props[(attributes[my_keys[0]], attributes[my_keys[1]])] = (
                    value
                )
            elif len(my_keys) == 3:
                my_props[
                    (
                        attributes[my_keys[0]],
                        attributes[my_keys[1]],
                        attributes[my_keys[2]],
                    )
                ] = value
            else:
                raise ValueError(
                    "XML property elements may contain only name, tag1, and "
                    f"tag2 attributes: {dict(attributes)!r}"
                )

        my_object.update_properties(my_props)


def _get_optional_property_value(name, value):
    if name in ("useability", "useable") and isinstance(value, str):
        normalized_value = value.strip().lower()
        if normalized_value == "true":
            return True
        if normalized_value == "false":
            return False

    return value
