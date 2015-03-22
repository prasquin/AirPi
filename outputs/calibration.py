"""A module to calibrate sensor data.

A module which is used to support calibration of sensors on an
individual basis. Calibration functions are specified in the AirPi
settings config file (usually AirPi/settings.cfg).

Note that this module does not output data or metadata, so the
output_data() and output_metadata() methods are inherited from the
parent class (Output), i.e. always return True.

"""

import output

class Calibration(output.Output):
    """A class to calibrate sensor data.

    A class which is used to support calibration of sensors on an
    individual basis. Calibration terms are specified in the AirPi
    settings config file (usually AirPi/settings.cfg).

    """

    requiredParams = []
    optionalParams = ["Light_Level", "Air_Quality", "Nitrogen_Dioxide",
                      "Carbon_Monoxide", "Volume", "UVI", "Bucket_tips"]
    sharedClass = None

    def __init__(self, params):
        """Initialise.

        Initialise the Calibration class, using the parameters passed in
        'params'. Note that the 'requiredParams' and 'optionalParams'
        are used to check that 'params' contains the appropriate
        options (this happens in define_plugin_params() in airpi.py
        after this object has been created).
        TODO: Move that functionality to the output.py module and let
              output plugins inherit it.

        Args:
            self: self.
            params: Parameters to be used in the initialisation.

        """
        self.calibrations = []
        self.calibrated = []
        self.lastuncalibrated = []
        for i in self.optionalParams:
            if i in params:
                [func, symb] = params[i].rsplit(',', 1)
                self.calibrations.append({'name': i,
                                            'function': eval("lambda x: " + func),
                                            'symbol': symb})

        if Calibration.sharedClass == None:
            Calibration.sharedClass = self

    def calibrate(self, datapoints):
        """Calibrate a set of data points.

        Calibrates a set of data points according to a correction
        function defined for the particular property being measured.

        Args:
            self: self.
            datapoints: The datapoints to be calibrated. This is usually
                        a dict containing another dict for each
                        property.

        """
        if datapoints == self.lastuncalibrated:
            # The same datapoints object, so the calculations would turn
            # out the same so we can just return the result of the last
            # calculations.
            return self.last

        self.calibrated = list(datapoints)
        # Recreate so we don't overwrite un-calibrated data:
        for i in range(0, len(self.last)):
            self.calibrated[i] = dict(self.calibrated[i]) # recreate again
            for j in self.calibrations:
                if self.calibrated[i]["name"] == j["name"]:
                    if self.calibrated[i]["value"] != None:
                        self.calibrated[i]["value"] = \
                            j["function"](self.calibrated[i]["value"])
                        self.calibrated[i]["symbol"] = j["symbol"]
        # Update which object we last worked on:
        self.lastuncalibrated = datapoints
        return self.calibrated

    def output_metadata(self):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. This particular plugin cannot output metadata, so this
        method will always return True. This is an abstract method of
        the Output class, which this class inherits from; this means you
        shouldn't (and can't) remove this method. See docs in the Output
        class for more info.

        Args:
            self: self.

        Returns:
            boolean True in all cases.
        """
        return True

    def findval(self, key):
        """Find (calibrated) data value for a given key.

        Find the data value for a given key; note this value will have
        been previously calibrated. This allows values to be extracted
        for use during other calibration operations (e.g. find the
        temperature so that the reading from another sensor can be
        compensated for temp).

        Args:
            self: self.
            key: string The property for which the value should be
                    obtained.

        Returns:
            The data value (previously calibrated).

        """
        found = 0
        num = 0
        for i in Calibration.sharedClass.calibrated:
            if i["name"] == key and i["value"] != None:
                found = found + i["value"]
                num += 1
        # Average for things like Temp. where we have multiple sensors:
        if num != 0:
            found = found / float(num)
        return found
