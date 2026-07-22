"""Module to handle a collection of species."""

from lvlspy.core.properties import Properties


class SpColl(Properties):
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

    def _sync_species_names(self):
        """Rebuild the internal mapping from each species' current name."""

        synced = {}
        for species in self.spcoll.values():
            species_name = species.get_name()
            if species_name in synced and synced[species_name] is not species:
                raise ValueError(
                    "Species collection contains multiple species with the "
                    f"name {species_name!r}"
                )
            synced[species_name] = species

        self.spcoll = synced

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

        self._sync_species_names()
        self.spcoll[species.get_name()] = species

    def remove_species(self, species):
        """Method to remove a species from a species collection.

        Args:
            ``species`` (:obj:`lvlspy.species.Species`) The species to be
            removed.

        Return:
        On successful return, the species has been removed.

        """

        self._sync_species_names()
        self.spcoll.pop(species.get_name())

    def get(self):
        """Method to retrieve the species collection as a dictionary.

        Returns:
            :obj:`dict`: A dictionary of the species.

        """

        self._sync_species_names()
        return self.spcoll

