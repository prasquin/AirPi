import RPi.GPIO as GPIO
import sensor

class raingauge(sensor.Sensor):
	requiredData = ["pinNumber"]
	optionalData = ["description"]
    
	def __init__(self, data):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		self.pinNum = int(data["pinNumber"])
		GPIO.setup(self.pinNum, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.pinNum, GPIO.FALLING, callback=self.bucketTip, bouncetime=300)
		self.rain = 0
		self.sensorName = "Maplin_N77NF"
		self.readingType = "pulseCount"
		self.valName = "Bucket_tips"
		self.valSymbol = ""
		self.valUnit = ""
		if "description" in data:
			self.description = data["description"]
		else:
			self.description = "A rain gauge."

	def getVal(self):
	        # return number of bucket tips since last reading
	        # that means we reset the count at this reading
		rain = self.rain
		self.rain = 0
		return rain

	def bucketTip(self, channel):
		self.rain += 1

