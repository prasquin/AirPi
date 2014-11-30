import sensor
import dhtreader
import time
import threading

# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_DHT_Driver_Python/dhtreader.c

class DHT22(sensor.Sensor):
    requiredData = ["measurement", "pinNumber"]
    optionalData = ["unit","description"]

    def __init__(self,data):
        """Initialise.

        Initialise the DHT22 sensor class using parameters passed in 'data'.
        Instances of this class can be set to monitor either temperature
        ('temp') or pressure ('h'). This is determined by the contents of
        'data' passed to this __init__ function. If you want to read both
        properties, you'll need two instances of the class.
        When set to read temperature, self.valName is 'Temperature-DHT' to
        differentiate it from other temperature sensors on the AirPi (such as
        the BMP). By default temperatures are read in Celsius; data["unit"]
        can be set to "F" to return readings in Fahrenheit instead if required.
        Humidity is returned as percentage relative humidity.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        Return:

        """
        dhtreader.init()
        dhtreader.lastDataTime = 0
        dhtreader.lastData = (None,None)
        self.sensorName = "DHT22"
        self.readingType = "sample"
        self.pinNum = int(data["pinNumber"])
        if "temp" in data["measurement"].lower():
            self.valName = "Temperature-DHT"
            self.valUnit = "Celsius"
            self.valSymbol = "C"
            if "unit" in data:
                if data["unit"] == "F":
                    self.valUnit = "Fahrenheit"
                    self.valSymbol = "F"
        elif "h" in data["measurement"].lower():
            self.valName = "Relative_Humidity"
            self.valSymbol = "%"
            self.valUnit = "% Relative Humidity"
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "A combined temperature and humidity sensor."
        return

    def getVal(self):
        """Get the current sensor value.

        Get the current sensor value, for either temperature or humidity
        (whichever is appropriate to this instance of the class).

        Args:
            self: self.

        Returns:
            float The current value for the sensor.

        """
        if (time.time() - dhtreader.lastDataTime) > 2: # ok to do another reading
            # launch & wait for thread
            th = DHTReadThread(self)
            th.start()
            th.join(2)
            if th.isAlive():
                raise Exception('Timeout reading ' + self.sensorName)
            dhtreader.lastDataTime = time.time()

        t, h = dhtreader.lastData
        if self.valName == "Temperature-DHT":
            temp = t
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
        elif self.valName == "Relative_Humidity":
            return h

# http://softwareramblings.com/2008/06/running-functions-as-threads-in-python.html
# https://docs.python.org/2/library/threading.html
class DHTReadThread(threading.Thread):
    def __init__(self, parent):
        self.parent = parent
        threading.Thread.__init__(self)

    def run(self):
        try:
            t, h = dhtreader.read(22,self.parent.pinNum)
        except Exception:
            t, h = dhtreader.lastData
        dhtreader.lastData = (t,h)
