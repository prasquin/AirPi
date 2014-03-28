import output
import datetime
import calibration

class Print(output.Output):
	requiredData = []
	optionalData = ["calibration"]

	def __init__(self,data):
		self.cal = calibration.Calibration.sharedClass
		self.docal = calibration.calCheck(data)

	def outputData(self,dataPoints):
		if self.docal == 1:
			dataPoints = self.cal.calibrate(dataPoints)

		print ""
		print "Time: " + str(datetime.datetime.now())
		for i in dataPoints:
			print i["name"] + ": " + str(i["value"]) + " " + i["symbol"]
		return True
