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
            toprint  = "Run started".ljust(23, '.') + metadata['STARTTIME'] + os.linesep
            toprint += "Operator".ljust(23, '.') + metadata['OPERATOR'] + os.linesep
            toprint += "Raspberry Pi name".ljust(23, '.') + metadata['PINAME'] + os.linesep
            toprint += "Raspberry Pi ID".ljust(23, '.') +  metadata['PIID'] + os.linesep
            toprint += "Sample frequency".ljust(23, '.') + metadata['SAMPLEFREQ'] + os.linesep
            if "AVERAGEFREQ" in metadata:
                toprint += "Averaging frequency".ljust(23, '.') + metadata['AVERAGEFREQ']
            print("==========================================================")
            print("Loading METADATA...")
            print(toprint)

    def outputData(self, dataPoints):
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
        	for i in dataPoints:
            		if i["name"] == "Location":
                		# print i["name"] + ": " + "Disposition:" + i["disposition"] + "Elevation: " + i["altitude"] + "Exposure: " + i["exposure"] + "Latitude: " + i["latitude"] + "Longitude: " + i["longitude"]
                		pprint(i)
            		else:
                                theValue = i["value"]
                                if type(theValue) is float:
                                    if theValue > 10000:
                                        theValue = int(round(i["value"], 0))
                                    elif theValue > 1000:
                                            theValue = round(i["value"], 1)
                                    else:
                                            theValue = round(i["value"], 2)
                                else:
                                        theValue = "-"
                                print (i["name"].ljust(17)).replace("_", " ") + ": " + str(theValue).ljust(8) + " " + i["symbol"].ljust(5) + "(" + i["readingType"] + ")"
                print "=========================================================="
        return True
