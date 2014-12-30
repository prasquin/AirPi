"""A template AirPi sensor plugin.

This file is a basic template which can be used as a base when creating
a custom AirPi sensor plugin. You should change the variable names and
function definitions as required, and also add plugin details to the file 
cfg/sensors.cfg"""

# All sensor plugins are sub-classes of sensor.
import sensor

class MySensorClass(sensor.Sensor):
    """A class to obtain data from an AirPi sensor.

    A class which is used to obtain data from an AirPi sensor.

    """

    # Parameters listed in requiredParams *MUST* be defined in sensors.cfg
    # Parameters listed in optionalParams can be defined in sensors.cfg if
    # appropriate, but are optional.
    requiredData = ["firstparamhere", "secondparamhere"]
    optionalData = ["xthparamhere","ythparamhere"]

    def __init__(self,data):
        """
        Initialisation.

        Any initialisation code goes here.
        """
        self.readingType = "sample"
        self.pinNum = int(data["pinNumber"])
        self.sensorName = "ABC123"
        self.valName = "Gas-I-Measure"
        self.valUnit = "Parts Per Million"
        self.valSymbol = "ppm"
        self.description = "An ABC123 sensor which measures a gas."
        return

    def getVal(self):
        """Get the current sensor value.

        Get the current sensor value.

        Args:
            self: self.

        Returns:
            float The current value for the sensor.

        """
        try:
            # temp = getValueSomehow()
        except TypeError as terr:
            # This will be thrown if the sensor fails to read,
            # and so 'temp' has type 'None'. That usually
            # happens at the start of the run, and is dealt with
            # either by the fact that it's a dummy run and we're
            # ignoring readings anyway, or by sample() in the
            # main airpi.py script (~ line 908).
            pass
        return temp