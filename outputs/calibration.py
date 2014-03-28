import output
import math
from string import rsplit

class Calibration(output.Output):
	requiredData = []
	optionalData = ["Light_Level", "Air_Quality", "Nitrogen_Dioxide", "Carbon_Monoxide", "Volume", "UVI", "Bucket_tips"]
	sharedClass = None

	def __init__(self,data):
		self.calibrations = []
		self.last = []
		for i in self.optionalData:
			if i in data:
				[f, s] = rsplit(data[i], ',', 1)
				self.calibrations.append({'name': i, 'function': eval("lambda x: " + f), 'symbol': s})

		if Calibration.sharedClass == None:
			Calibration.sharedClass = self

	def calibrate(self,dataPoints):
		# turn this into some sort of caching so we don't have to re-run the calculation?
		self.last = dataPoints
		for i in range(0, len(dataPoints)):
			for j in self.calibrations:
				if dataPoints[i]["name"] == j["name"]:
					dataPoints[i]["value"] = j["function"](dataPoints[i]["value"])
					dataPoints[i]["symbol"] = j["symbol"]
		return dataPoints

def findVal(key):
	found = 0
	num = 0
	for i in Calibration.sharedClass.last:
		if i["name"] == key:
			found = found + i["value"]
			num += 1
	# average for things like Temperature where we have multiple sensors
	found = found / float(num)
	return found

def calCheck(data):
	if "calibration" in data:
		if data["calibration"].lower() in ["on","true","1","yes"]:
			return 1
		else:
			return 0
	else:
		return 0
