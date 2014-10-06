import mcp3008
import sensor

class Analogue(sensor.Sensor):
    requiredData = ["adcPin", "measurement", "sensorName"]
    optionalData = ["pullUpResistance", "pullDownResistance", "sensorVoltage", "description"]
    
    def __init__(self, data):
        """Initialise.

        Initialise the generic Analogue sensor class using parameters passed
        in 'data'. The MCP3008 ADC is used by this class, and output can be in
        either Ohms or millivolts depending on the exact sensor in question.

        Args:
            self: self.
            data: A dict containing the parameters to be used during setup.

        """
        self.adc = mcp3008.MCP3008.sharedClass
        self.adcPin = int(data["adcPin"])
        self.valName = data["measurement"]
        self.sensorName = data["sensorName"]
        self.readingType = "sample"
        self.pullUp, self.pullDown = None, None
        if "pullUpResistance" in data:
            self.pullUp = int(data["pullUpResistance"])
        if "pullDownResistance" in data:
            self.pullDown = int(data["pullDownResistance"])
        if "sensorVoltage" in data:
            self.sensorVoltage = int(data["sensorVoltage"])
        else:
            self.sensorVoltage = 3.3
        class ConfigError(Exception): pass
        if self.pullUp != None and self.pullDown != None:
            print "Please choose whether there is a pull up or pull down resistor for the " + self.valName + " measurement by only entering one of them into the settings file"
            raise ConfigError
        self.valUnit = "Ohms"
        self.valSymbol = "Ohms"
        if self.pullUp == None and self.pullDown == None:
            self.valUnit = "millvolts"
            self.valSymbol = "mV"
        if "description" in data:
            self.description = data["description"]
        else:
            self.description = "An analogue sensor."
        
    def getVal(self):
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
        result = self.adc.readADC(self.adcPin)
        if result == 0:
            print "Error: Check wiring for the " + self.sensorName + " measurement, no voltage detected on ADC input " + str(self.adcPin)
            return None
        if result == 1023 or result == 1022:
            print "Error: Check wiring for the " + self.sensorName + " measurement, full voltage detected on ADC input " + str(self.adcPin)
            return None
        vout = float(result)/1023 * 3.3
        
        if self.pullDown != None:
            resOut = (self.pullDown * self.sensorVoltage) / vout - self.pullDown
        elif self.pullUp != None:
            resOut = self.pullUp / ((self.sensorVoltage / vout) - 1)
        else:
            resOut = vout * 1000
        return resOut
        
