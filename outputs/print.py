import output
import datetime
import time
import calibration
import os

class Print(output.Output):
    requiredParams = ["format"]
    optionalParams = ["calibration", "metadata"]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
	self.format = params["format"]

    def outputMetadata(self):
        metadata = self.getMetadata()
        toprint  = "Run started: " + metadata['starttime'] + os.linesep
        toprint += "Operator: " + metadata['operator'] + os.linesep
        toprint += "Raspberry Pi name: " + metadata['piname'] + os.linesep
        toprint += "Raspberry Pi ID: " +  metadata['piid']
        return toprint

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
                                print (i["name"].ljust(17)).replace("_", " ") + ": " + str(theValue).ljust(8) + " " + i["symbol"]
                print "=========================================================="
        return True
