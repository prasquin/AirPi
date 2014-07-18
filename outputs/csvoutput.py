#!/usr/bin/env python

import output
import datetime
import time
import calibration
import socket

class CSVOutput(output.Output):
	requiredData = ["outputFile"]
	optionalData = ["calibration"]

	def __init__(self,data):
		if "<date>" in data["outputFile"]:
                        filenamedate = time.strftime("%Y%m%d-%H%M")
                        data["outputFile"] = data["outputFile"].replace("<date>", filenamedate)
 		if "<hostname>" in data["outputFile"]:
                        if socket.gethostname().find('.')>=0:
                                filenamehost = socket.gethostname()
                        else:
                                filenamehost = socket.gethostbyaddr(socket.gethostname())[0]
                	data["outputFile"] = data["outputFile"].replace("<hostname>", filenamehost)
		# open the file persistently for append
		self.file = open(data["outputFile"], "a")
		# write a header line so we know which sensor is which?
		self.header = False;
		self.cal = calibration.Calibration.sharedClass
		self.docal = calibration.calCheck(data)

	def outputData(self,dataPoints):
		if self.docal == 1:
			dataPoints = self.cal.calibrate(dataPoints)

		line = "\"" + str(datetime.datetime.now()) + "\"," + str(time.time())
		if self.header == False:
			header = "\"Date and time\",\"Unix time\"";

		for i in dataPoints:
			if self.header == False:
				header = "%s,\"%s %s (%s) (%s)\"" % (header, i["sensor"], i["name"], i["symbol"], i["readingType"])
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
