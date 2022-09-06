import numpy as np

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

    def update_energy(self, energy, units = 'keV'):
        """Method to update the energy for a level.

        Args:
            ``energy`` (:obj:`float`):  The new energy for the level.

            ``units`` (:obj:`str`, optional):  A string giving the
            units for the energy.

        Returns:
            On successful return, the energy has been updated.

        """

        self.energy = units_dict[units] * energy

    def update_multiplicity(self):
        """Method to update the multiplicity for a level.

        Args:
            ``multiplicity`` (:obj:`int`):  The new multiplicity for the level.

        Returns:
            On successful return, the multiplicity has been updated.

        """

        self.multiplicity = multiplicity
