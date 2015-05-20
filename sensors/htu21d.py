""" Read data from the HTU21D sensor.

A high-level Class to read data from the HTU21D I2C sensor. An instance of
the Class can read *either* temperature *or* humidity; see __init__()
for more detail. 

You must add these lines in sensors.cfg:
[HTU21D-temp]
filename = htu21d
enabled = yes
measurement = temp

[HTU21D-hum]
filename = htu21dÒ
enabled = yes
measurement = humidity

"""

import sensor
import htuBackend
import os

class HTU21D(sensor.Sensor):
    htuClass = None
    requiredData = ["measurement"]
    optionalData = ["unit", "description"]
    
    def __init__(self, data):
        """Initialise HTU21D sensor class.

        Initialise the HTU21D sensor class using parameters passed in 'data'.
        Instances of this class can be set to monitor either temperature
        ('temp') or humidity ('hum'). This is determined by the contents of
        'data' passed to this __init__ function. If you want to read both
        properties, you'll need two instances of the class.
        When set to read temperature, self.valName is 'Temperature-HTU' to
        differentiate it from other temperature sensors on the AirPi (such as
        the DHT22). By default temperatures are read in Celsius; data["unit"]
        can be set to "F" to return readings in Fahrenheit instead if required.
        Humidity is returned as percentage relative humidity.
        The I2C bus number depending of the version of the PCB is auto detected.
        The access to I2C doesn't need smbus library and so no need of the Adafruit
        library.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        Return:

        """
        self.readingType = "sample"
        if "temp" in data["measurement"].lower():
            self.sensorName = "HTU21D-temp"
            self.valName = "Temperature-HTU"
            self.valUnit = "Celsius"
            self.valSymbol = "C"
            if "unit" in data:
                if data["unit"] == "F":
                    self.valUnit = "Fahrenheit"
                    self.valSymbol = "F"
        elif "h" in data["measurement"].lower():
            self.sensorName = "HTU21D-hum"
            self.valName = "Humidity-HTU"
            self.valUnit = "% Relative Humidity"
            self.valSymbol = "%"
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "A I2C combined temperature and humidity sensor."
        if (HTU21D.htuClass == None):
            #HTU21D.htuClass = htuBackend.HTU21D(bus = int(data["i2cbus"]))
            i2cbus = 0
           if os.path.exists("/dev/i2c-1"): #test which i2c bus ID is present
              i2cbus = 1
            HTU21D.htuClass = htuBackend.HTU21D(bus = i2cbus)
        return

    def getVal(self):
        """Get the current sensor value.

        Get the current sensor value, for either temperature or pressure
        (whichever is appropriate to this instance of the class).

        Args:
            self: self.

        Returns:
            float The current value for the sensor.

        """
        if self.valName == "Temperature-HTU":
            temp = HTU21D.htuClass.readTemperature()
            if self.valUnit == "Fahrenheit":
                try:
                    temp = temp * 1.8 + 32
                except TypeError as terr:
                    # This will be thrown if the sensor fails to read,
                    # and so 'temp' has type 'None'. That usually
                    # happens at the start of the run, and is dealt with
                    # either by the fact that it's a dummy run and we're
                    # ignoring readings anyway, or by sample() in the
                    # main airpi.py script (~ line 908).
                    pass
            return temp
        elif self.valName == "Humidity-HTU":
            return HTU21D.htuClass.readHumidity()
