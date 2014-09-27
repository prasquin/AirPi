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
        if self.metadatareqd:
            print("==========================================================")
            print("Loading METADATA...")
            toprint  = "Run started".ljust(23, '.') + metadata['STARTTIME'] + os.linesep
            toprint += "Operator".ljust(23, '.') + metadata['OPERATOR'] + os.linesep
            toprint += "Raspberry Pi name".ljust(23, '.') + metadata['PINAME'] + os.linesep
            toprint += "Raspberry Pi ID".ljust(23, '.') +  metadata['PIID'] + os.linesep
            toprint += "Sample frequency".ljust(23, '.') + metadata['SAMPLEFREQ']
            if "AVERAGEFREQ" in metadata:
                toprint += os.linesep + "Averaging frequency".ljust(23, '.') + metadata['AVERAGEFREQ'] + os.linesep
            print(toprint)

    def output_data(self, dataPoints):
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        if self.format == "csv":
            theOutput = "\"" + time.strftime("%Y-%m-%d %H:%M:%S") + "\","
            for i in dataPoints:
                theOutput += str(i["value"]) + ","
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
                    value = "{0:.1f}".format(point["value"])
                    print (point["name"].ljust(17)).replace("_", " ") + ": " + str(value).rjust(8) + " " + point["symbol"].ljust(5) + "(" + point["readingType"] + ")"
            print "=========================================================="
        return True

    def format_output_gps(self, prop, value, unit):
        return str(prop.ljust(17) + ": " + str("{0:.2f}".format(value)).rjust(8) + " " + unit)