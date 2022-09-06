import numpy as np
from lxml import etree

units_dict = {'eV': 1000, 'keV': 1, 'MeV': 1.e-3, 'GeV': 1.e-6}

class Level():
    """A class for storing and retrieving data about a level.

    Args:
        ``energy`` (:obj:`float`): The energy of the level.  It is in units
        given by the keyword `units`.

        ``multiplicity`` (:obj:`int`): The multiplicity of the level.
        given by the keyword `units`.

        ``units`` (:obj:`str`, optional):  A string giving the
        units for the energy.

    """

    def __init__(self, energy, multiplicity, units = 'keV'):
        self.energy = energy / units_dict[units]
        self.multiplicity = multiplicity
        self.units = 'keV'

    def get_energy(self, units = 'keV'):
        """Method to retrieve the energy for a level.

        Args:
            ``units`` (:obj:`str`, optional):  A string giving the
            units for the energy.

        Returns:
            :obj:`float`: The energy.

        """

        return units_dict[units] * self.energy

    def get_multiplicity(self):
        """Method to retrieve the multiplicity for a level.

        Returns:
            :obj:`int`: The multiplicity.

        """

        return self.multiplicity

class Species():
    """A class for storing and retrieving data about a species.

    Args:
        ``name`` (:obj:`str`): The name of the species.

        ``levels`` (:obj:`list`, optional): A list of tuples giving the energy
        and multiplicty of the levels of the species.

        ``units`` (:obj:`str`, optional):  A string giving the
        units for the energy.

    """

    def __init__(self, name):
        self.name = name
        self.levels = []

    def __init__(self, name, levels, units = 'keV'):
        self.name = name
        self.levels = []
        for level in levels:
            self.levels.append(Level(level[0], level[1], units = units))

    def get_levels(self):
        return self.levels 
