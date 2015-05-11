"""
Generic class to support analogue sensors.

The MCP3008 ADC is used by this class, and output can be in
either Ohms or millivolts depending on the exact sensor in question.

"""
import mcp3008
import sensor

class Analogue(sensor.Sensor):
    """ The MCP3008 ADC is used by this class, and output can be in
    either Ohms or millivolts depending on the exact sensor in question.

    """
    requiredData = ["adcpin", "measurement", "sensorname"]
    optionalData = ["pullupResistance", "pulldownResistance", "sensorvoltage", "description"]

    def __init__(self, data):
        """Initialise.

        Initialise the generic Analogue sensor class using parameters passed
        in 'data'.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        """
        self.adc = mcp3008.MCP3008.sharedClass
        self.adcpin = int(data["adcpin"])
        self.valname = data["measurement"]
        self.sensorname = data["sensorname"]
        self.readingtype = "sample"
        self.pullup, self.pulldown = None, None
        if "pullupResistance" in data:
            self.pullup = int(data["pullupResistance"])
        if "pulldownResistance" in data:
            self.pulldown = int(data["pulldownResistance"])
        if "sensorvoltage" in data:
            self.sensorvoltage = int(data["sensorvoltage"])
        else:
            self.sensorvoltage = 3.3

        class ConfigError(Exception):
            """ Exception to raise if no pullup or pulldown value."""
            pass

        if self.pullup != None and self.pulldown != None:
            msg = "Please choose whether there is a pull up or pull down"
            msg += " resistor for the " + self.valname + " measurement by only"
            msg += " entering one of them into the settings file"
            print(msg)
            raise ConfigError
        self.valunit = "Ohms"
        self.valsymbol = "Ohms"
        if self.pullup == None and self.pulldown == None:
            self.valunit = "millvolts"
            self.valsymbol = "mV"
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "An analogue sensor."

    def getval(self):
        """Get the current sensor value.

        Get the current sensor value, in either Ohms or millivolts depending
        on the exact sensor. Includes a 'sense check' to identify
        potential errors with full or no voltage.

        Args:
            self: self.

        Returns:
            float The current value for the sensor.
            None If there is potentially an error with the data.

        """
        result = self.adc.readadc(self.adcpin)
        if result == 0:
            msg = "Error: Check wiring for the " + self.sensorname
            msg += " measurement, no voltage detected on ADC input "
            msg += str(self.adcpin)
            print(msg)
            return None
        if result == 1023 and self.sensorname != "LDR":
            msg = "Error: Check wiring for the " + self.sensorname
            msg += " measurement, full voltage detected on ADC input "
            msg += str(self.adcpin)
            print(msg)
            return None
        vout = float(result)/1023 * 3.3

        if self.pulldown != None:
            resout = (self.pulldown * self.sensorvoltage) / vout - self.pulldown
        elif self.pullup != None:
            resout = self.pullup / ((self.sensorvoltage / vout) - 1)
        else:
            resout = vout * 1000
        return resout
