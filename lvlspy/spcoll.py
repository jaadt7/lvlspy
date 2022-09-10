import numpy as np
from lxml import etree
import lvlspy.props as lp


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

    def write_to_xml(self, file, pretty_print=True):
        """Method to write the collection to XML.

        Args:
            ``file`` (:obj:`str`) The output file name.

            ``pretty_print`` (:obj:`bool`, optional): If set to True,
            routine outputs the xml in nice indented format.

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
                my_energy = etree.SubElement(my_level_props, "energy")
                my_energy.text = str(level.get_energy())
                my_multiplicity = etree.SubElement(my_level_props, "multiplicity")
                my_multiplicity.text = str(level.get_multiplicity())

                if level.get_energy() in tu_dict:

                    if len(tu_dict[level.get_energy()]) > 0:
                        my_transitions = etree.SubElement(my_level, "transitions")
                        for transition in tu_dict[level.get_energy()]:
                            my_trans = etree.SubElement(my_transitions, "transition")
                            self._add_optional_properties(my_trans, transition)
                            lower_level = transition.get_lower_level()
                            my_to_energy = etree.SubElement(my_trans, "to_energy")
                            my_to_energy.text = str(lower_level.get_energy())
                            my_to_multiplicity = etree.SubElement(
                                my_trans, "to_multiplicity"
                            )
                            my_to_multiplicity.text = str(
                                lower_level.get_multiplicity()
                            )
                            my_a = etree.SubElement(my_trans, "a")
                            my_a.text = str(transition.get_Einstein_A())

        xml.write(file, pretty_print=pretty_print)

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
