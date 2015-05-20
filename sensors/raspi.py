""" Read data from Raspberry Pi sensors.

A high-level Class to read data from the Raspberry Pi sensor and data, which
provides cpu temperature, cpu usage and memory usage readings.

You need to install required support packages:
sudo apt-get install python-psutil

You must add these lines in sensors.cfg:
[RasPi-temp]
filename = raspi
enabled = yes
measurement = temp

[RasPi-cpu]
filename = raspi
enabled = yes
measurement = cpu

[RasPi-mem]
filename = raspi
enabled = yes
measurement = mem

"""

import sensor
import os

class raspi(sensor.Sensor):
    requiredData = ["measurement"]
    optionalData = ["unit", "description"]
    
    def __init__(self, data):
        """Initialise RasPi sensor class.

        Initialise the RasPi sensor class using parameters passed in 'data'.
        Instances of this class can be set to monitor either temperature
        ('temp') or cpu usage ('cpu') or memory ram usage (mem).
        This is determined by the contents of 'data' passed to this __init__ 
        function. If you want to read both properties, you'll need two instances
        of the class.
        When set to read temperature, self.valName is 'RasPi-temp' to
        differentiate it from other temperature sensors on the AirPi (such as
        the DHT22). By default temperatures are read in Celsius; data["unit"]
        can be set to "F" to return readings in Fahrenheit instead if required.
        CPU usage and memory usage is returned as percentage.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        Return:

        """
        self.readingType = "sample"
        if "temp" in data["measurement"].lower():
            self.sensorName = "RasPi-temp"
            self.valName = "Temp-RaspPi"
            self.valUnit = "Celsius"
            self.valSymbol = "C"
            if "unit" in data:
                if data["unit"] == "F":
                    self.valUnit = "Fahrenheit"
                    self.valSymbol = "F"
        elif "cpu" in data["measurement"].lower():
            self.sensorName = "RasPi-cpu"
            self.valName = "CPU Usage-RasPi"
            self.valUnit = "%"
            self.valSymbol = "%"
        elif "mem" in data["measurement"].lower():
            self.sensorName = "RasPi-mem"
            self.valName = "Mem Usage-RasPi"
            self.valUnit = "%"
            self.valSymbol = "%"
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "A Raspberry Pi combined temperature sensor, CPU and memory usage."

    def getVal(self):
        """Get the current sensor value.

        Get the current sensor value, for either temperature or pressure
        (whichever is appropriate to this instance of the class).

        Args:
            self: self.

        Returns:
            float The current value for the sensor.

        """
        if self.valName == "Temp-RaspPi":
            file = open('/sys/class/thermal/thermal_zone0/temp','r')
            temp = round(float(file.read())/1000,2)
            file.close()
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
        elif self.valName == "CPU Usage-RasPi":
            # 1:user, 3:system, 5:nice, 7:idle
	        file = os.popen('top -n1')
	        i = 0
            while True:
                i += 1
                line = file.readline()
                if i == 3:
 	                data = line.split()
 	            return 100-float(data[7])	
        elif self.valName == "Mem Usage-RasPi":
            # 3:total 5:used, 7:free
            file = os.popen('free')
            i = 0
            while True:
                i += 1
                line = file.readline()
                if i == 2:
                    data = line.split()
                    return round(float(data[2])/float(data[1])*100,2)
        else:
            print("Error: Raspberry sensor/data name error")
            return False
