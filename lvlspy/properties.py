class Properties:
    """A class for storing and retrieving optional properties."""

    def __init__(self):
        self.properties = {}

    def get_properties(self):
        """Method to retrieve the optional properties.

        Returns:
            :obj:`dict`: The dictionary of current properties.

        """

        return self.properties

    def update_properties(self, properties):
        """Method to update the optional properties.

        Args:
            ``properties`` (:obj:`dict`):  A dictionary of properties.
            New properties are added.  Old properties are updated.

        Returns:
            On successful return, the properties have been updated.

        """

        self.properties = {**self.properties, **properties}
