import output
import datetime
import time

class Print(output.Output):
	requiredData = ["outputFile"]
	optionalData = []

	def __init__(self,data):
		# open the file persistently for append
		self.file = open(data["outputFile"], "a")
		# write a header line so we know which sensor is which?
		self.header = False;

	def outputData(self,dataPoints):
		line = "\"" + str(datetime.datetime.now()) + "\"," + time.time()
		if self.header == False:
			header = "\"Date and time\",\"Unix time\"";

		for i in dataPoints:
			if self.header == False:
				header = "%s,\"%s (%s)\"" % (header, i["name"], i["symbol"])
			line = line + "," + str(i["value"])

		# if it's the first write of this instance do a header so we know what's what
		if self.header == False:
			self.file.write(header + "\n")
			self.header = True
		# write the data line to the file
		self.file.write(line + "\n")
		# don't forget to flush the file in case of power failure
		self.file.flush()
		return True

	#need an exit hook to close the file nicely
	def __del__(self):
		self.file.flush()
		self.file.close()
