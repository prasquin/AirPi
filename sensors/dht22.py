import sensor
import dhtreader
import time
import threading

# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_DHT_Driver_Python/dhtreader.c

class DHT22(sensor.Sensor):
	requiredData = ["measurement", "pinNumber"]
	optionalData = ["unit","description"]
	def __init__(self,data):
		dhtreader.init()
		dhtreader.lastDataTime = 0
		dhtreader.lastData = (None,None)
		self.sensorName = "DHT22"
		self.readingType = "sample"
		self.pinNum = int(data["pinNumber"])
		if "temp" in data["measurement"].lower():
			self.valName = "Temperature"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			if "unit" in data:
				if data["unit"] == "F":
					self.valUnit = "Fahrenheit"
					self.valSymbol = "F"
		elif "h" in data["measurement"].lower():
			self.valName = "Relative Humidity"
			self.valSymbol = "%"
			self.valUnit = "% Relative Humidity"
		if "description" in data:
			self.description = data["description"]
		else:
			self.description = "A combined temperature and humidity sensor."
		return

	def getVal(self):
		if (time.time() - dhtreader.lastDataTime) > 2: # ok to do another reading
			# launch & wait for thread
			th = DHTReadThread(self)
			th.start()
			th.join(2)
			if th.isAlive():
				raise Exception('Timeout reading ' + self.sensorName)
			dhtreader.lastDataTime = time.time()

		t, h = dhtreader.lastData
		if self.valName == "Temperature":
			temp = t
			if self.valUnit == "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp
		elif self.valName == "Relative Humidity":
			return h

# http://softwareramblings.com/2008/06/running-functions-as-threads-in-python.html
# https://docs.python.org/2/library/threading.html
class DHTReadThread(threading.Thread):
	def __init__(self, parent):
		self.parent = parent
		threading.Thread.__init__(self)

	def run(self):
		try:
			t, h = dhtreader.read(22,self.parent.pinNum)
		except Exception:
			t, h = dhtreader.lastData
		dhtreader.lastData = (t,h)
