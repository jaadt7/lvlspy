"""
Module to handle ENSDF input and output
"""

class ENSDF:
    """
    A class for handling the reading from and writing to ENSDF
    """

    def update_from_ensdf(self,coll, file, sp_list):
        """Method to update a species collection from an ENSDF file.

        Args:
            ``coll`` (:obj: `obj') The collection to be read from the ENSDF file

            ``file`` (:obj:`str`) The name of the XML file from which to update.

            ``sp_list`` (:obj:`list`, optional): List of species to be read from file.
              Defaults to all species.

        Returns:
            On successful return, the species collection has been updated.

        """

        if sp_list == []:
            self._read_whole_file(coll,file)

        else:
            for sp in sp_list:
                self._get_species_from_ensdf(coll, file, sp)
    
    