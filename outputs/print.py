"""A module to print AirPi data to screen.

A module which is used to output data from an AirPi onto screen (or more
accurately, stdout). This can include GPS data if present, along with
metadata (again, if present).

"""

import output
import datetime
import time
import calibration
import os
#from geopy.geocoders import Nominatim

class Print(output.Output):
    """A module to print AirPi data to screen.

    A module which is used to output data from an AirPi onto screen (or more
    accurately, stdout). This can include GPS data if present, along with
    metadata (again, if present).

    """

    requiredParams = ["format"]
    optionalParams = ["calibration", "limits", "metadatareqd"]

    def __init__(self, params, limits = False):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkcal(params)
        self.limits = limits
        self.format = params["format"]
        self.metadatareqd = params["metadatareqd"]

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        if self.metadatareqd:
            print("==========================================================")
            print("Loading: METADATA")
            toprint = "Run started".ljust(23, '.')
            toprint += metadata['STARTTIME']
            toprint += os.linesep + "Operator".ljust(23, '.')
            toprint += metadata['OPERATOR']
            toprint += os.linesep + "Raspberry Pi name".ljust(23, '.')
            toprint += metadata['PINAME']
            toprint += os.linesep + "Raspberry Pi ID".ljust(23, '.')
            toprint += metadata['PIID']
            toprint += os.linesep + "Sample frequency".ljust(23, '.')
            toprint += metadata['SAMPLEFREQ']
            if 'AVERAGEFREQ' in metadata:
                toprint += os.linesep + "Averaging frequency".ljust(23, '.')
                toprint += metadata['AVERAGEFREQ']
            if 'DUMMYDURATION' in metadata:
                toprint += os.linesep + "Initialising runs".ljust(23, '.')
                toprint += metadata['DUMMYDURATION']
            if 'STOPAFTER' in metadata:
                toprint += os.linesep + "Stopping after".ljust(23, '.')
                toprint += metadata['STOPAFTER']
            print(toprint)

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
        if self.format == "csv":
            theoutput = "\"" + sampletime.strftime("%Y-%m-%d %H:%M:%S,%f") + "\","
            breach = None
            for point in datapoints:
                if point["name"] == "Location":
                    props = ["latitude",
                                "longitude",
                                "altitude",
                                "exposure",
                                "disposition"]
                    for prop in props:
                        theoutput += str(point[prop]) + ","
                else:
                    theoutput += str(point["value"]) + ","
                    if self.limits and self.limits.isbreach(point):
                        if breach is None:
                            breach = "BREACHES: "
                        breach += point["name"] + ","
            if breach:
                theoutput += breach
            theoutput = theoutput[:-1]
            print(theoutput)
        else:
            print("Time".ljust(17) + ": " + sampletime.strftime("%Y-%m-%d %H:%M:%S.%f"))
            for point in datapoints:
                if point["name"] == "Location":
                    print(self.format_output_gps("Loc - Latitude",
                                                    point["latitude"], "deg"))
                    print(self.format_output_gps("Loc - Longitude",
                                                    point["longitude"], "deg"))
                    print(self.format_output_gps("Loc - Altitude",
                                                    point["altitude"], "m"))
                    disp = (("Loc - Disp./Exp.").ljust(17)).replace("_", " ")
                    disp += ": " + str(point["disposition"].title()) + ", "
                    disp += point["exposure"].title().ljust(8)
                    #TODO: Finish reverse geocode
                    #geolocator = Nominatim()
                    #disp += geolocator.reverse(point["latitude"], point["longitude"])
                    print(disp)
                else:
                    value = "{0:.2f}".format(point["value"])
                    line = (point["name"].ljust(17)).replace("_", " ")
                    line += ": " + str(value).rjust(10) + " "
                    line += point["symbol"].ljust(5) + "("
                    line += point["readingtype"] + ")"
                    if self.limits and self.limits.isbreach(point):
                        line += " BREACH!"
                    print(line)
            print("==========================================================")
        return True

    def format_output_gps(self, prop, value, unit):
        """Format GPS output nicely.

        Format one GPS datapoint to display nicely on a single line. A
        single datapoint could be, for example, 'latitude', or
        alternatively 'longitude'.

        Args:
            self: self.
            prop: The name of the property being measured.
            value: The value of the property being measured.
            unit: string The unit in which the value is measured.

        Returns:
            string The formatted value.

        """
        value = str(prop.ljust(17)) + ": "
        value += str("{0:.2f}".format(value).rjust(10) + " " + unit)
