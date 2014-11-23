class Sensor():
    def __init__(self, data):
        raise NotImplementedError

    def get_name(self):
        """Get Class name.

        Get the name of the class. Lots of Classes inherit from Sensor,
        so this varies depending on which one we're looking at.

        Returns:
            string The class name.

        """
        return self.__class__.__name__

    def get_sensor_name(self):
        """Get Sensor name.

        Get the human-friendly name of the sensor. Lots of Classes
        inherit from Sensor, so this varies depending on which one we're
        looking at.

        Returns:
            string The sensor name.

        """
        return self.valName