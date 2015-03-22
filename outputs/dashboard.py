"""A module to print AirPi data to screen.

A module which is used to output data from an AirPi onto screen (or more
accurately, stdout). This does not include GPS or metadata.

"""

import output
import calibration
import limits

class Dashboard(output.Output):
    """A module to print AirPi data to screen.

    A module which is used to output data from an AirPi onto screen (or more
    accurately, stdout). This does not include GPS or metadata.

    """

    requiredParams = ["limits"]
    optionalParams = ["calibration"]

    def __init__(self, params, limits = None):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkcal(params)
        self.limits = limits

    def output_metadata(self, metadata = None):
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

    def output_data(self, datapoints, sampletime):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present
        a dict containing one value and associated properties such as
        units and symbols, while the latter presents a dict containing
        several readings such as latitude, longitude and altitude, but
        no units or symbols.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            sampletime: datetime representing the time the sample was taken.

        Returns:
            boolean True if data successfully printed to stdout.

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)
        print("Time".ljust(17) + ": " + sampletime.strftime("%Y-%m-%d %H:%M:%S.%f"))
        for point in datapoints:
            if point["name"] in ["Nitrogen_Dioxide", "Carbon_Monoxide"]:
                if self.limits.isbreach(point):
                    colour = '\033[41m'
                else:
                    colour = '\033[42m'
                print(point["name"].ljust(17).replace("_", " ") + ": " + colour + " " + '\033[0m')
        print("==========================================================")
        return True
