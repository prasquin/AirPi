import output
import datetime
import time
import calibration

class Print(output.Output):
    requiredData = ["format"]
    optionalData = ["calibration"]

    def __init__(self,data):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(data)
	self.format = data["format"]

    def outputData(self,dataPoints):
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        if self.format == "csv":
		theOutput = "\"" + time.strftime("%Y-%m-%d %H:%M:%S") + "\","
        	for i in dataPoints:
	                theOutput += str(round(i["value"],2)) + ","
                theOutput = theOutput[:-1]
                print theOutput
	else:
        	print "========================================================"
        	print ("Time".ljust(17)) + ": " + time.strftime("%Y-%m-%d %H:%M:%S")
        	for i in dataPoints:
            		if i["name"] == "Location":
                		# print i["name"] + ": " + "Disposition:" + i["disposition"] + "Elevation: " + i["altitude"] + "Exposure: " + i["exposure"] + "Latitude: " + i["latitude"] + "Longitude: " + i["longitude"]
                		pprint(i)
            		else:
                		print (i["name"].ljust(17)) + ": " + str(i["value"]) + " " + i["symbol"]
        return True
