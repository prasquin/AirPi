import output
import datetime
import time
import calibration
import os

class Print(output.Output):
    requiredParams = ["format"]
    optionalParams = ["calibration", "metadatareqd"]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
        self.format = params["format"]
        self.metadatareqd = params["metadatareqd"]

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this plugin.
        Metadata is set in airpi.py and then passed as a dict to each plugin
        which wants to output it.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        if self.metadatareqd:
            print("==========================================================")
            print("Loading: METADATA")
            toprint  = "Run started".ljust(23, '.') + metadata['STARTTIME']
            toprint += os.linesep + "Operator".ljust(23, '.') + metadata['OPERATOR']
            toprint += os.linesep + "Raspberry Pi name".ljust(23, '.') + metadata['PINAME']
            toprint += os.linesep + "Raspberry Pi ID".ljust(23, '.') +  metadata['PIID']
            toprint += os.linesep + "Sample frequency".ljust(23, '.') + metadata['SAMPLEFREQ']
            if 'STOPAFTER' in metadata:
                toprint += os.linesep + "Stopping after".ljust(23, '.') + metadata['STOPAFTER']
            if 'AVERAGEFREQ' in metadata:
                toprint += os.linesep + "Averaging frequency".ljust(23, '.') + metadata['AVERAGEFREQ']
            print(toprint)

    def output_data(self, dataPoints):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration is
        carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present a dict
        containing one value and associated properties such as units and
        symbols, while the latter presents a dict containing several readings
        such as latitude, longitude and altitude, but no units or symbols.

        Args:
            self: self.
            dataPoints: A dict containing the data to be output.

        """
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        if self.format == "csv":
            theOutput = "\"" + time.strftime("%Y-%m-%d %H:%M:%S") + "\","
            for point in dataPoints:
                if point["name"] == "Location":
                    props=["latitude", "longitude", "altitude", "exposure", "disposition"]
                    for prop in props:
                        theOutput += str(point[prop]) + ","
                else:
                    theOutput += str(point["value"]) + ","
            theOutput = theOutput[:-1]
            print theOutput
        else:
            print ("Time".ljust(17)) + ": " + time.strftime("%Y-%m-%d %H:%M:%S")
            for point in dataPoints:
                if point["name"] == "Location":
                    print(self.format_output_gps("Loc - Latitude", point["latitude"], "deg"))
                    print(self.format_output_gps("Loc - Longitude", point["longitude"], "deg"))
                    print(self.format_output_gps("Loc - Altitude", point["altitude"], "m"))
                    print(("Loc - Disp./Exp.").ljust(17)).replace("_", " ") + ": " + str(point["disposition"].title() + ", " + point["exposure"].title()).ljust(8)
                else:
                    value = "{0:.2f}".format(point["value"])
                    print (point["name"].ljust(17)).replace("_", " ") + ": " + str(value).rjust(10) + " " + point["symbol"].ljust(5) + "(" + point["readingType"] + ")"
            print "=========================================================="
        return True

    def format_output_gps(self, prop, value, unit):
        """Format GPS output nicely.

        Format GPS output to display nicely.

        Args:
            self: self.
            prop: The name of the property being measured.
            value: The value of the property.
            unit: string The unit in which the value is measured.

        """
        return str(prop.ljust(17) + ": " + str("{0:.2f}".format(value)).rjust(10) + " " + unit)