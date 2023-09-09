"""Module to handle a collection of species."""

import os
import sys
from lxml import etree
import lvlspy.properties as lp
import lvlspy.species as ls
import lvlspy.level as lv
import lvlspy.transition as lt


class SpColl(lp.Properties):
    """A class for storing and retrieving data about a species collection.

    Args:
        ``species`` (:obj:`list`, optional): A list of individual
        :obj:`lvlspy.species.Species` objects.

    """

    def __init__(self, species=None):
        super().__init__()
        self.properties = {}
        self.spcoll = {}
        if species:
            for my_species in species:
                self.spcoll[my_species.get_name()] = my_species

    def add_species(self, species):
        """Method to add a species to a collection.

        Args:
            ``species`` (:obj:`lvlspy.species.Species`) The species to be
            added.

        Return:
            On successful return, the species has been added.  If the species
            previously existed in the collection, it has been replaced with
            the new species.

        """

        self.spcoll[species.get_name()] = species

    def remove_species(self, species):
        """Method to remove a species from a species collection.

        Args:
            ``species`` (:obj:`lvlspy.species.Species`) The species to be
            removed.

        Return:
            On successful return, the species has been removed.

        """

        self.spcoll.pop(species.get_name())

    def get(self):
        """Method to retrieve the species collection as a dictionary.

        Returns:
            :obj:`dict`: A dictionary of the species.

        """

        return self.spcoll

    def write_to_xml(self, file, pretty_print=True, units="keV"):
        """Method to write the collection to XML.

        Args:
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

        self._add_optional_properties(root, self)

        for species_name, species in self.get().items():
            my_species = etree.SubElement(root, "species", name=species_name)

            self._add_optional_properties(my_species, species)

            xml_levels = etree.SubElement(my_species, "levels")

            for level in species.get_levels():
                self._add_level_to_xml(xml_levels, species, level, units)

        xml.write(file, pretty_print=pretty_print)

    def _add_level_to_xml(self, xml_levels, species, level, units):
        result = etree.SubElement(xml_levels, "level")
        self._add_optional_properties(result, level)
        result_props = etree.SubElement(result, "properties")
        if units != "keV":
            my_energy = etree.SubElement(result_props, "energy", units=units)
        else:
            my_energy = etree.SubElement(result_props, "energy")
        my_energy.text = self._get_energy_text(level.get_energy(), units)
        my_multiplicity = etree.SubElement(result_props, "multiplicity")
        my_multiplicity.text = str(level.get_multiplicity())

        self._add_transitions_to_xml(result, species, level, units)

        return result

    def _add_transitions_to_xml(self, xml_level, species, level, units):

        lower_levels = species.get_lower_linked_levels(level)

        if len(lower_levels) == 0:
            return

        xml_transitions = etree.SubElement(xml_level, "transitions")

        for lower_level in lower_levels:
            transition = species.get_level_to_level_transition(
                level, lower_level
            )
            xml_trans = etree.SubElement(xml_transitions, "transition")
            self._add_optional_properties(xml_trans, transition)
            if units != "keV":
                xml_to_energy = etree.SubElement(
                    xml_trans, "to_energy", units=units
                )
            else:
                xml_to_energy = etree.SubElement(xml_trans, "to_energy")
            xml_to_energy.text = self._get_energy_text(
                lower_level.get_energy(), units
            )
            xml_to_multiplicity = etree.SubElement(
                xml_trans, "to_multiplicity"
            )
            xml_to_multiplicity.text = str(lower_level.get_multiplicity())
            xml_a = etree.SubElement(xml_trans, "a")
            xml_a.text = str(transition.get_einstein_a())

    def _get_energy_text(self, energy, units):
        return str(energy * lv.units_dict[units])

    def _add_optional_properties(self, my_element, my_object):
        my_props = my_object.get_properties()

        if len(my_props):
            props = etree.SubElement(my_element, "optional_properties")
            for prop in my_props:
                if isinstance(prop, str):
                    my_prop = etree.SubElement(props, "property", name=prop)
                elif isinstance(prop, tuple):
                    if len(prop) == 2:
                        my_prop = etree.SubElement(
                            props, "property", name=prop[0], tag1=prop[1]
                        )
                    elif len(prop) == 3:
                        my_prop = etree.SubElement(
                            props,
                            "property",
                            name=prop[0],
                            tag1=prop[1],
                            tag2=prop[2],
                        )
                else:
                    print("Improper property key")
                    sys.exit()

                my_prop.text = str(my_props[prop])

    def _update_optional_properties(self, my_element, my_object):
        opt_props = my_element.xpath("optional_properties")

        if len(opt_props) > 0:
            props = opt_props[0].xpath("property")

            my_props = {}
            for prop in props:
                attributes = prop.attrib
                my_keys = attributes.keys()
                if len(my_keys) == 1:
                    my_props[attributes[my_keys[0]]] = prop.text
                elif len(my_keys) == 2:
                    my_props[
                        (attributes[my_keys[0]], attributes[my_keys[1]])
                    ] = prop.text
                elif len(my_keys) == 3:
                    my_props[
                        (
                            attributes[my_keys[0]],
                            attributes[my_keys[1]],
                            attributes[my_keys[2]],
                        )
                    ] = prop.text
                else:
                    print("Improper keys for property")
                    sys.exit()

            my_object.update_properties(my_props)

    def validate(self, file):
        """Method to validate a species collection XML file.

        Args:
            ``file`` (:obj:`str`) The name of the XML file to validate.

        Returns:
            An error message if invalid and nothing if valid.

        """

        parser = etree.XMLParser(remove_blank_text=True)
        xml = etree.parse(file, parser)
        xml.xinclude()

        schema_file = os.path.join(
            os.path.dirname(__file__), "xsd_pub/spcoll.xsd"
        )
        xmlschema_doc = etree.parse(schema_file)

        xml_validator = etree.XMLSchema(xmlschema_doc)
        xml_validator.validate(xml)

    def update_from_xml(self, file, xpath=""):
        """Method to update a species collection from an XML file.

        Args:
            ``file`` (:obj:`str`) The name of the XML file from which to update.

            ``xpath`` (:obj:`str`, optional): XPath expression to select
            species.  Defaults to all species.

        Returns:
            On successful return, the species collection has been updated.

        """

        parser = etree.XMLParser(remove_blank_text=True)
        xml = etree.parse(file, parser)
        xml.xinclude()

        spcoll = xml.getroot()

        self._update_optional_properties(spcoll, self)

        for xml_species in spcoll.xpath("//species" + xpath):
            self.add_species(self._get_species_from_xml(xml_species))

    def _get_species_from_xml(self, xml_species):
        level_dict = {}
        result = ls.Species(xml_species.attrib["name"])
        self._update_optional_properties(xml_species, result)
        for xml_level in xml_species.xpath(".//level"):
            new_level = self._get_level_from_xml(xml_level)
            result.add_level(new_level)
            level_dict[new_level.get_energy()] = new_level

            for xml_trans in xml_level.xpath(".//transition"):
                trans = self._get_transition_from_xml(
                    xml_trans, new_level, level_dict
                )
                if trans:
                    result.add_transition(trans)

        return result

    def _get_level_from_xml(self, xml_level):
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
        self._update_optional_properties(xml_level, result)

        return result

    def _get_transition_from_xml(self, xml_trans, upper_level, level_dict):
        to_energy = xml_trans.xpath(".//to_energy")
        to_a = xml_trans.xpath(".//a")

        f_to_energy = self._convert_to_kev(to_energy)
        if f_to_energy in level_dict:
            result = lt.Transition(
                upper_level,
                level_dict[f_to_energy],
                float(to_a[0].text),
            )
            self._update_optional_properties(xml_trans, result)
            return result
        return None

    def _convert_to_kev(self, energy):
        attributes = energy[0].attrib
        result = float(energy[0].text)
        if "units" in attributes:
            result /= lv.units_dict[attributes["units"]]
        return result
