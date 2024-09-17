"""Module to handle a collection of species."""

import lvlspy.io as lio
import lvlspy.properties as lp


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
        """Link to IO to write the collection to XML.

        Args:
            ``file`` (:obj:`str`) The output file name.

            ``pretty_print`` (:obj:`bool`, optional): If set to True,
            routine outputs the xml in nice indented format.

            ``units`` (:obj:`str`, optional): A string for the energy units.

        Return:
            On successful return, the species collection data have been
            written to the XML output file.

        """

        lio.XML().write_to_xml(self, file, pretty_print, units)

    def validate(self, file):
        """Link to IO to validate a species collection XML file.

        Args:
            ``file`` (:obj:`str`) The name of the XML file to validate.

        Returns:
            An error message if invalid and nothing if valid.

        """
        lio.XML().validate(file)

    def update_from_xml(self, file, xpath=""):
        """Link to update a species collection from an XML file.

        Args:
            ``file`` (:obj:`str`) The name of the XML file from which to update.

            ``xpath`` (:obj:`str`, optional): XPath expression to select
            species.  Defaults to all species.

        Returns:
            On successful return, the species collection has been updated.

        """
        lio.XML().update_from_xml(self, file, xpath)

    def update_from_ensdf(self, file, sp):
        """Link to update a species collection from ENSDF file

        Args:
            ``file`` (:obj:`str`) The file name from which to update.

            ``sp`` (:obj:`str`) The name of the species to be read in.

        Returns:
            On successful return, the species collection has been updated.

        """

        lio.ENSDF().update_from_ensdf(self, file, sp)

    def write_to_ensdf(self, file_name):
        """Link to write a species collection to an ENSDF file

        Args:
            ``file_name`` (:obj:`str`) The name of ENSDF file to be written to.

        Returns:
            On successful return, the species collection has been written

        """
        lio.ENSDF().write_to_ensdf(self, file_name)
