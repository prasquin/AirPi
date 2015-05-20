""" Read data from Domoticz BMP085/180 sensor.

A high-level Class to read data from the Domoticz sensors, which
provides barometric (air pressure) and temperature readings.

You must insert these lines in sensor.cfg:
[Domo-temp]
filename = domoticzs
enabled = yes
measurement = temp
URL = http://192.168.1.2:8080
IDX = 10

[Domo-pres]
filename = domoticzs
enabled = yes
measurement = pres
URL = http://192.168.1.2:8080
IDX = 10
mslp = on
altitude = 20

"""

import sensor
import requests
import math

class domoticzs(sensor.Sensor):
    requiredData = ["measurement","URL","IDX"]
    optionalData = ["altitude","mslp","unit","description"]
    
    def __init__(self, data):
        """Initialise the Domoticz sensors class using parameters passed in 'data'.
        Instances of this class can be set to monitor either temperature
        ('temp') or pressure ('pres'). This is determined by the contents of
        'data' passed to this __init__ function. If you want to read both
        properties, you'll need two instances of the class.
        When set to read temperature, self.valName is 'Temperature-Domo' to
        differentiate it from other temperature sensors on the AirPi (such as
        the DHT22). By default temperatures are read in Celsius; data["unit"]
        can be set to "F" to return readings in Fahrenheit instead if required.
        Pressures are returned in Hectopascals. If data["altitude"] is provided,
        and data["mslp"] is true, then Mean Sea Level Pressure will be returned
        by getVal() instead of absolute local pressure.
        URL is IP adress of the domoticz system. IDX is the ID of the BMP085/BMP180
        sensor or another sensor of your Domoticz. Depending of the king of sensor 
        you must set to True or to set to False data["mslp"], in case it take in
        consideration the Mean Sea Level Pressure

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        Return:

        """
        self.readingType = "sample"
        self.URL = data["URL"]
        self.IDX = data["IDX"]
        if "temp" in data["measurement"].lower():
            self.sensorName = "Domo-temp"
            self.valName = "Temperature-Domo"
            self.valUnit = "Celsius"
            self.valSymbol = "C"
            if "unit" in data:
                if data["unit"] == "F":
                    self.valUnit = "Fahrenheit"
                    self.valSymbol = "F"
        elif "pres" in data["measurement"].lower():
            self.sensorName = "Domo-pres"
            self.valName = "Pressure-Domo"
            self.valUnit = "Hectopascal"
            self.valSymbol = "hPa"
            self.altitude = 0
            self.mslp = False
            if "mslp" in data:
                if data["mslp"].lower() in ["on", "true", "1", "yes"]:
                    self.mslp = True
                    if "altitude" in data:
                        self.altitude = data["altitude"]
                    else:
                        msg = "To calculate MSLP, please provide an 'altitude' (in m)"
                        print(msg)
                        self.mslp = False
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "Domoticz combined temperature and pressure sensor."
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
        req = self.URL + '/json.htm?type=devices&rid='+ self.IDX
        try:
            r = requests.get(req, timeout=1)     # timeout 1 sec.
        except requests.exceptions.RequestException:
            print ("Error: Domoticz server not found")
            return False
        if r.status_code != 200:
            print ("Error: Domoticz message",r.text)
            print ("Error: Domoticz URL", req)
            return False
        else:
            domojson = r.json()
            result = domojson.get('result')
            if self.valName == "Temperature-Domo":
                for i,v in enumerate(result):
                    temp = domojson['result'][i]['Temp']
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
            elif self.valName == "Pressure-Domo":
                for i,v in enumerate(result):
                    pres = domojson['result'][i]['Barometer']
                if self.mslp:
                    T0 = float(self.altitude) / 44330
                    T1 = math.pow(1 - T0, 5.255)
                    pres = pres / T1
                return pres
