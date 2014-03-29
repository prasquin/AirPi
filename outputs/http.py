import output
import os
import BaseHTTPServer
from datetime import datetime
from threading import Thread
from string import replace
import calibration

# useful resources:
# http://unixunique.blogspot.co.uk/2011/06/simple-python-http-web-server.html
# http://docs.python.org/2/library/simplehttpserver.html
# http://docs.python.org/2/library/basehttpserver.html#BaseHTTPServer.BaseHTTPRequestHandler
# https://wiki.python.org/moin/BaseHttpServer
# http://stackoverflow.com/questions/10607621/a-simple-website-with-python-using-simplehttpserver-and-socketserver-how-to-onl
# http://www.huyng.com/posts/modifying-python-simplehttpserver/
# http://stackoverflow.com/questions/6391280/simplehttprequesthandler-override-do-get

class HTTP(output.Output):
	requiredData = ["wwwPath"]
	optionalData = ["port", "history", "title", "about", "calibration"]

	details = """
<div class="panel panel-default">
	<div class="panel-heading">
		<h4 class="panel-title"><a class="accordion-toggle collapsed" data-toggle="collapse" data-parent="#accordion" href="#collapse-$sensorId$">
			$readingName$: $reading$ ($units$)
		</a></h4>
	</div>
	<div id="collapse-$sensorId$" class="panel-collapse collapse">
		<div class="panel-body"><p>
			Sensor: <em>$sensorName$</em><br/>
			Description: <em>$sensorText$</em>
		</p></div>
	</div>
</div>""";

	rssItem = "<item><title>$sensorName$</title><description>$reading$ $units$</description></item>\n"

	def __init__(self,data):
		self.www = data["wwwPath"]

		if "port" in data:
			self.port = int(data["port"])
		else:
			self.port = 8080

		if "history" in data:
			if data["history"].lower() in ["off","false","0","no"]:
				self.history = 0
			elif os.path.isfile(data["history"]):
				#it's a file to load, check if it exists
				self.history = 2
				self.historyFile = data["history"];
			else:
				# short-term history
				self.history = 1
		else:
			self.history = 0

		if "title" in data:
			self.title = data["title"]
		else:
			self.title = "AirPi"

		if "about" in data:
			self.about = data["about"]
		else:
			self.about = "An AirPi weather station."

		self.cal = calibration.Calibration.sharedClass
		self.docal = calibration.calCheck(data)
		self.sensorIds = []

		self.handler = requestHandler
		self.server = httpServer(self, ("", self.port), self.handler)
		self.thread = Thread(target = self.server.serve_forever)
		self.thread.daemon = True
		self.thread.start()

		# load up history
		if self.history == 2:
			print "Loading history from " + self.historyFile

	def createSensorIds(self,dataPoints):
		if len(self.sensorIds) == 0:
			for i in dataPoints:
				self.sensorIds.append(i["sensor"]+" "+i["name"])

	def getSensorId(self,name):
		for i in range(0,len(self.sensorIds)):
			if name == self.sensorIds[i]:
				return i
		return -1

	def outputData(self,dataPoints):
		if self.docal == 1:
			dataPoints = self.cal.calibrate(dataPoints[:])
		self.createSensorIds(dataPoints)		

		self.data = dataPoints
		self.lastUpdate = str(datetime.now())
		return True

class httpServer(BaseHTTPServer.HTTPServer):

	def __init__(self, httpoutput, server_address, RequestHandlerClass):
		self.httpoutput = httpoutput
		BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)


class requestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		if self.path == '/' or self.path == '/index.html':
			self.path = 'index.html'
			index = 1
		else:
			index = 0
		if self.path == '/rss.xml':
			rss = 1
		else:
			rss = 0

		toread = self.server.httpoutput.www + os.sep + self.path
		if os.path.isfile(toread):
			pageFile = open(toread, 'r')
			page = pageFile.read()
			pageFile.close()
			response = 200
		else:
			page = "quoth the raven, 404"
			response = 404

		# do substitutions here
		if index == 1 and response == 200:
			page = replace(page, "$title$", self.server.httpoutput.title)
			page = replace(page, "$about$", self.server.httpoutput.about)
			page = replace(page, "$time$", self.server.httpoutput.lastUpdate)
			# sort out the sensor stuff
			details = ''
			for i in self.server.httpoutput.data:
				line = replace(self.server.httpoutput.details, "$readingName$", i["name"])
				line = replace(line, "$reading$", str(round(i["value"], 2)))
				line = replace(line, "$units$", i["symbol"])
				line = replace(line, "$sensorId$", str(self.server.httpoutput.getSensorId(i["sensor"]+" "+i["name"])))
				line = replace(line, "$sensorName$", i["sensor"])
				line = replace(line, "$sensorText$", i["description"])
				details += line
			if self.server.httpoutput.history != 0:
				page = replace(page, "$graph$", "\"graph_\"+id+\".html\"")
			else:
				page = replace(page, "$graph$", "\"No history available.\"")
			page = replace(page, "$details$", details)
		elif rss == 1 and response == 200:
			page = replace(page, "$title$", self.server.httpoutput.title)
			page = replace(page, "$about$", self.server.httpoutput.about)
			page = replace(page, "$time$", self.server.httpoutput.lastUpdate)
			items = ''
			for i in self.server.httpoutput.data:
				line = replace(self.server.httpoutput.rssItem, "$sensorName$", i["name"])
				line = replace(line, "$reading$", str(i["value"]))
				line = replace(line, "$units$", i["symbol"])
				items += line
			page = replace(page, "$items$", items)

		self.send_response(response)
		if response == 200:
			fileName, fileExtension = os.path.splitext(toread)
			if fileExtension == '.png':
				self.send_header("Content-Type", "image/png")
			elif fileExtension == '.css':
				self.send_header("Content-Type", "text/css")
			elif fileExtension == '.js':
				self.send_header("Content-Type", "application/javascript")
			elif fileExtension == '.rss':
				self.send_header("Content-Type", "application/rss+xml")
			else:
				self.send_header("Content-Type", "text/html")
		else:
			self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", len(page))
		self.end_headers()
		self.wfile.write(page)
		self.wfile.close()
