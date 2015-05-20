""" Read data from the DS1820 sensor.

A high-level Class to read data from the DS18B20 sensor. This  An instance of
the Class can read temperature; see __init__() for more detail.
For more info about sensor: www.adafruit.com/product/381

You must add these lines in /etc/modules
w1-gpio
w1-thermbelow 

You must add this line to the bottom of /boot/config.txt
dtoverlay=w1-gpio

You must add these lines in sensors.cfg:
[DS18B20]          #if several DS18B20 sensor, increment as [DS18B20-1], [DS18B20-2] ...
filename = ds18b20
enabled = yes
id = 28-00047620aabb    #see the sensors id in /sys/bus/w1/devices
name = Temperature-DS   #if several DS18B20 sensors, the name must be unique
measurement = temp

"""

import sensor
import dsBackend
import os

class DS18B20(sensor.Sensor):
    dsClass = None
    requiredData = ["measurement","id"]
    optionalData = ["name","unit","description"]
    
    def __init__(self, data):
        """Initialise DS18B20 sensor class.

        Initialise the DS18B20 sensor class using parameters passed in 'data'.
        Instances of this class can be set to monitor either temperature
        ('temp')
        When set to read temperature, self.valName is 'Temperature-DS' to
        differentiate it from other temperature sensors on the AirPi (such as
        the DHT22). By default temperatures are read in Celsius; data["unit"]
        can be set to "F" to return readings in Fahrenheit instead if required.
        The 1-Wire bus is supported by Raspbian so it's use the GPIO pin 4
        the same for the DHT22. You cannot use these sensors together.
        You can use several DS18B20 sensor together in paralel, using the same
        GPIO pin 4 and one pull-up resistor of 4.7K
        
        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        Return:

        """
        self.readingType = "sample"
        self.sensorName = "DS18B20-temp"
        if "name" in data:
            self.valName = data["name"]
        else:
            self.valName = "Temperature-DS"
        self.valUnit = "Celsius"
        self.valSymbol = "C"
        if "unit" in data:
            if data["unit"] == "F":
                self.valUnit = "Fahrenheit"
                self.valSymbol = "F"
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "A 1-Wire temperature sensor."
        if (DS18B20.dsClass == None):
            DS18B20.dsClass = dsBackend.DS18B20(id = data["id"])
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
       
        temp = DS18B20.dsClass.readTemperature()
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
