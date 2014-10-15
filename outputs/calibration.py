"""A module to calibrate sensor data.

A module which is used to support calibration of sensors on an
individual basis. Calibration terms are specified in the AirPi settings
config file (usually AirPi/settings.cfg).

"""

import output
import math

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
        options.

        Args:
            self: self.
            params: Parameters to be used in the initialisation.

        """
        self.calibrations = []
        self.last = []
        self.lastpassed = []
        for i in self.optionalParams:
            if i in params:
                [f, s] = params[i].rsplit(',', 1)
                self.calibrations.append({'name': i,
                                            'function': eval("lambda x: " + f),
                                            'symbol': s})

        if Calibration.sharedClass == None:
            Calibration.sharedClass = self

    def calibrate(self, dataPoints):
        """Calibrate a set of data points.

        Calibrates a set of data points according to a correction
        function defined for the particular property being measured.

        Args:
            self: self.
            dataPoints: The dataPoints to be calibrated. This is usually
                        a dict containing another dict for each
                        property.

        """
        if self.lastpassed == dataPoints:
            # The same dataPoints object, so the calculations would turn
            # out the same so we can just return the result of the last
            # calculations.
            return self.last

        self.last = list(dataPoints) 
        # Recreate so we don't overwrite un-calibrated data:
        for i in range(0, len(self.last)):
            self.last[i] = dict(self.last[i]) # recreate again
            for j in self.calibrations:
                if self.last[i]["name"] == j["name"]:
                    if self.last[i]["value"] != None:
                        self.last[i]["value"] = \
                            j["function"](self.last[i]["value"])
                        self.last[i]["symbol"] = j["symbol"]
        # Update which object we last worked on:
        self.lastpassed = dataPoints
        return self.last

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it. Even if it is not
        appropriate for the output plugin to output metadata, this
        method is required because airpi.py looks for it in its own
        output_metadata() method. In such cases, this method will simply
        return boolean True.

        Args:
            self: self.
            metadata: A dict containing the metadata for the run.

        """
        return True

    def output_data(self, dataPoints):
        """Output data.

        Output data in the format stipulated by the plugin. Even if it
        is not appropriate for the plugin to output data (e.g. for the
        'calibration' plugin), this method is required because airpi.py
        looks for it in when setting up plugins. In such cases, this
        method will simply return boolean True.

        Args:
            self: self.
            dataPoints: A dict containing the data to be output.

        """
        return True

    def findVal(self, key):
        """Find data value for a given key.

        Find the data value for a given key. This allows values to be
        extracted for use during calibration (e.g. find the temperature
        so that the reading from another sensor can be compensated for
        temp).

        Args:
            self: self.
            key: string The property for which the value should be
                    obtained.

        """
        found = 0
        num = 0
        for i in Calibration.sharedClass.last:
            if i["name"] == key and i["value"] != None:
                found = found + i["value"]
                num += 1
        # Average for things like Temp. where we have multiple sensors:
        if num != 0:
            found = found / float(num)
        return found
