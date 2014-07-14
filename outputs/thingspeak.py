import output
import requests
import calibration

class Thingspeak(output.Output):
	requiredData = ["APIKey"]
	optionalData = ["calibration"]

	def __init__(self,data):
		self.APIKey=data["APIKey"]
		self.cal = calibration.Calibration.sharedClass
		self.docal = calibration.calCheck(data)

	def outputData(self,dataPoints):
		if self.docal == 1:
			dataPoints = self.cal.calibrate(dataPoints)
		arr ={} 
		counter = 1
		for i in dataPoints:
			if i["value"] != None: #this means it has no data to upload.
				arr["field" + str(counter)] = round(i["value"],2)
			counter += 1
		url = "https://api.thingspeak.com/update?key="+self.APIKey
		try:
			z = requests.get(url, params=arr)
			if z.text=="0": 
				print "ThingSpeak Error: " + z.text
				print "URL: " + z.url
				return False
		except Exception:
			return False
		return True
