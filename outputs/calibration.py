import output

class Calibration(output.Output):
	requiredData = []
	optionalData = ["Light_Level"]
	sharedClass = None

	def __init__(self,data):
		self.calibrations = []
		for i in self.optionalData:
			if i in data:
				self.calibrations.append({'name': i, 'function': data[i]})

		if Calibration.sharedClass == None:
			Calibration.sharedClass = self

	def calibrate(self,dataPoints):
		for i in range(0, len(dataPoints)):
			for j in self.calibrations:
				if dataPoints[i]["name"] == j["name"]:
					print j["function"]
		return dataPoints


def calCheck(data):
	if "calibration" in data:
		if data["calibration"].lower() in ["on","true","1","yes"]:
			return 1
		else:
			return 0
	else:
		return 0
