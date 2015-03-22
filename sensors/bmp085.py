""" Read data from BMP085 sensor.

A high-level Class to read data from the Bosch BMP085 sensor, which
provides barometric (air pressure) and temperature readings. Requires
the bmpBackend Class to read the raw data from the sensor.

"""
import sensor
import bmpBackend

class BMP085(sensor.Sensor):
    """ Read data from BMP085 sensor.

    A high-level Class to read data from the Bosch BMP085 sensor, which
    provides barometric (air pressure) and temperature readings. Requires
    the bmpBackend Class to read the raw data from the sensor.

    """

    bmpClass = None
    requiredData = ["measurement", "i2cbus"]
    optionalData = ["altitude", "mslp", "unit", "description"]

    def __init__(self, data):
        """Initialise BMP085 sensor class.

        Initialise the BMP085 sensor class using parameters passed in 'data'.
        Instances of this class can be set to monitor either temperature
        ('temp') or pressure ('pres'). This is determined by the contents of
        'data' passed to this __init__ function. If you want to read both
        properties, you'll need two instances of the class.
        When set to read temperature, self.valname is 'Temperature-BMP' to
        differentiate it from other temperature sensors on the AirPi (such as
        the DHT22). By default temperatures are read in Celsius; data["unit"]
        can be set to "F" to return readings in Fahrenheit instead if required.
        Pressures are returned in Hectopascals. If data["altitude"] is provided,
        and data["mslp"] is true, then Mean Sea Level Pressure will be returned
        by getval() instead of absolute local pressure.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        Return:

        """
        self.readingtype = "sample"
        if "temp" in data["measurement"].lower():
            self.sensorname = "BMP085-temp"
            self.valname = "Temperature-BMP"
            self.valunit = "Celsius"
            self.valsymbol = "C"
            if "unit" in data:
                if data["unit"] == "F":
                    self.valunit = "Fahrenheit"
                    self.valsymbol = "F"
        elif "pres" in data["measurement"].lower():
            self.sensorname = "BMP085-pres"
            self.valname = "Pressure"
            self.valsymbol = "hPa"
            self.valunit = "Hectopascal"
            self.altitude = 0
            self.mslp = False
            if "mslp" in data:
                if data["mslp"].lower() in ["on", "true", "1", "yes"]:
                    self.mslp = True
                    if "altitude" in data:
                        self.altitude = data["altitude"]
                    else:
                        msg = "To calculate MSLP, please provide an 'altitude'"
                        msg += " (in m) for the BMP085 pressure module."
                        print(msg)
                        self.mslp = False
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "BOSCH combined temperature and pressure sensor."
        if BMP085.bmpClass == None:
            BMP085.bmpClass = bmpBackend.BMP085(bus=int(data["i2cbus"]))
        return

    def getval(self):
        """Get the current sensor value.

        Get the current sensor value, for either temperature or pressure
        (whichever is appropriate to this instance of the class).

        Args:
            self: self.

        Returns:
            float The current value for the sensor.

        """
        if self.valname == "Temperature-BMP":
            temp = BMP085.bmpClass.readtemperature()
            if self.valunit == "Fahrenheit":
                try:
                    temp = temp * 1.8 + 32
                except TypeError:
                    # This will be thrown if the sensor fails to read,
                    # and so 'temp' has type 'None'. That usually
                    # happens at the start of the run, and is dealt with
                    # either by the fact that it's a dummy run and we're
                    # ignoring readings anyway, or by sample() in the
                    # main airpi.py script (~ line 908).
                    pass
            return temp
        elif self.valname == "Pressure":
            # Multiply by 0.01 to convert to Hectopascals
            if self.mslp:
                return BMP085.bmpClass.readmslpressure(self.altitude) * 0.01
            else:
                return BMP085.bmpClass.readpressure() * 0.01
