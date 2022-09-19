import numpy as np
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
        self.properties = {}
        self.spcoll = {}
        if species:
            for sp in species:
                self.spcoll[sp.get_name()] = sp

    def add_species(self, species):
        """Method to add a species to a collection.

        Args:
            ``species`` (:obj:`lvlspy.species.Species`) The species to be added.

        Return:
            On successful return, the species has been added.

        """

        self.spcoll[species.get_name()] = species

    def remove_species(self, species):
        """Method to remove a species from a species collection.

        Args:
            ``species`` (:obj:`lvlspy.species.Species`) The species to be removed.

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

        my_coll = self.get()

        for sp in my_coll:

            tu_dict = {}

            for transition in my_coll[sp].get_transitions():
                e_upper = (transition.get_upper_level()).get_energy()

                if e_upper not in tu_dict:
                    tu_dict[e_upper] = []

                tu_dict[e_upper].append(transition)

            my_species = etree.SubElement(root, "species", name=sp)

            self._add_optional_properties(my_species, my_coll[sp])

            my_levels = etree.SubElement(my_species, "levels")

            levels = my_coll[sp].get_levels()

            for level in levels:
                my_level = etree.SubElement(my_levels, "level")
                self._add_optional_properties(my_level, level)
                my_level_props = etree.SubElement(my_level, "properties")
                if units != "keV":
                    my_energy = etree.SubElement(my_level_props, "energy", units=units)
                else:
                    my_energy = etree.SubElement(my_level_props, "energy")
                my_energy.text = self._get_energy_text(level.get_energy(), units)
                my_multiplicity = etree.SubElement(my_level_props, "multiplicity")
                my_multiplicity.text = str(level.get_multiplicity())

                if level.get_energy() in tu_dict:

                    if len(tu_dict[level.get_energy()]) > 0:
                        my_transitions = etree.SubElement(my_level, "transitions")
                        for transition in tu_dict[level.get_energy()]:
                            my_trans = etree.SubElement(my_transitions, "transition")
                            self._add_optional_properties(my_trans, transition)
                            lower_level = transition.get_lower_level()
                            if units != "keV":
                                my_to_energy = etree.SubElement(
                                    my_trans, "to_energy", units=units
                                )
                            else:
                                my_to_energy = etree.SubElement(my_trans, "to_energy")
                            my_to_energy.text = self._get_energy_text(
                                lower_level.get_energy(), units
                            )
                            my_to_multiplicity = etree.SubElement(
                                my_trans, "to_multiplicity"
                            )
                            my_to_multiplicity.text = str(
                                lower_level.get_multiplicity()
                            )
                            my_a = etree.SubElement(my_trans, "a")
                            my_a.text = str(transition.get_Einstein_A())

        xml.write(file, pretty_print=pretty_print)

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
                            props, "property", name=prop[0], tag1=prop[1], tag2=prop[2]
                        )
                else:
                    print("Improper property key")
                    exit()

                my_prop.text = my_props[prop]

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
                    exit()

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

        url = "http://liblvls.sourceforge.net/xsd_pub/2022-09-10/spcoll.xsd"

        xml_validator = etree.XMLSchema(file=url)
        xml_validator.assert_(xml)

    def update_from_xml(self, file):
        """Method to update a species collection from an XML file.

        Args:
            ``file`` (:obj:`str`) The name of the XML file from which to update.

        Returns:
            On successful return, the species collection has been updated.

        """

        parser = etree.XMLParser(remove_blank_text=True)
        xml = etree.parse(file, parser)
        xml.xinclude()

        spcoll = xml.getroot()

        self._update_optional_properties(spcoll, self)

        el_species = spcoll.xpath("//species")

        species = []

        for sp in el_species:
            level_dict = {}
            my_species = ls.Species(sp.attrib["name"])
            self._update_optional_properties(sp, my_species)
            el_level = sp.xpath(".//level")
            for lev in el_level:
                props = lev.xpath(".//properties")
                energy = props[0].xpath(".//energy")
                multiplicity = props[0].xpath(".//multiplicity")
                attributes = energy[0].attrib
                if "units" in attributes:
                    my_level = lv.Level(
                        float(energy[0].text),
                        int(multiplicity[0].text),
                        units=attributes["units"],
                    )
                else:
                    my_level = lv.Level(
                        float(energy[0].text), int(multiplicity[0].text)
                    )
                self._update_optional_properties(lev, my_level)

                level_dict[my_level.get_energy()] = my_level

                my_species.add_level(my_level)

                el_trans = lev.xpath(".//transition")
                for trans in el_trans:
                    to_energy = trans.xpath(".//to_energy")
                    to_multiplicity = trans.xpath(".//to_multiplicity")
                    to_a = trans.xpath(".//a")

                    f_to_energy = self._convert_to_keV(to_energy)
                    if f_to_energy in level_dict:
                        my_trans = lt.Transition(
                            my_level, level_dict[f_to_energy], float(to_a[0].text)
                        )
                        self._update_optional_properties(trans, my_trans)
                        my_species.add_transition(my_trans)

            self.add_species(my_species)

    def _convert_to_keV(self, energy):
        attributes = energy[0].attrib
        result = float(energy[0].text)
        if "units" in attributes:
            result /= lv.units_dict[attributes["units"]]
        return result
