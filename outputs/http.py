import output
import os
import BaseHTTPServer
from datetime import datetime
from threading import Thread
from string import replace

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
	optionalData = ["port", "history", "title", "about"]

	tableRow = '<tr><td>$sensorName$</td><td>$reading$ $units$</td><td><div class="btn pull-right" id="$sensorId$-button">Details &raquo;</div></td></tr>\n';
	sensorDetails = '<div class="span6 hidden" id="$sensorId$"><h4>$sensorName$</h4><p>$sensorText$</p><p><a class="btn pull-right btn-primary" href="#">History</a></p></div>\n';
	detailsJSstart = "$('#$sensorId$-button').click(function() {\n"
	detailsJSshow = "$('#$sensorId$').removeClass('hidden');\n"
	detailsJShide = "$('#$sensorId$').addClass('hidden');\n"
	detailsJSend = "});\n"

	def __init__(self,data):
		self.www = data["wwwPath"]

		if "port" in data:
			self.port = int(data["port"])
		else:
			self.port = 8080

		if "history" in data:
			if data["history"].lower in ["off","false","0","no"]:
				self.history = 0
			else:
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

		self.handler = requestHandler
		self.server = httpServer(self, ("", self.port), self.handler)
		self.thread = Thread(target = self.server.serve_forever)
		self.thread.daemon = True
		self.thread.start()

	def outputData(self,dataPoints):
		self.data = dataPoints
		self.lastUpdate = str(datetime.now())
		return True

class httpServer(BaseHTTPServer.HTTPServer):

	def __init__(self, httpoutput, server_address, RequestHandlerClass):
		self.httpoutput = httpoutput
		BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)


class requestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		if self.path == '/' or self.path == 'index.html':
			self.path = 'index.html'
			index = 1
		else:
			index = 0

		toread = self.server.httpoutput.www + os.sep + self.path
		if os.path.isfile(toread):
			pageFile = open(toread, 'r')
			page = pageFile.read()
			pageFile.close()
			response = 200
		else:
			page = "quoth the raven, 404"
			response = 404


#tableRow = '<tr><td>$sensorName$</td><td>$reading$ $units$</td><td><div class="btn pull-right" id="$sensorId$-button">Details &raquo;</div></td></tr>\n';
#sensorDetails = '<div class="span6 hidden" id="$sensorId$"><h4>$sensorName$</h4><p>$sensorText$</p><p><a class="btn pull-right btn-primary" href="#">History</a></p></div>\n';
#detailsJSstart = "$('#$sensorId$-button').click(function() {"
#detailsJSshow = "$('#$sensorId$').removeClass('hidden');"
#detailsJShide = "$('#$sensorId$').addClass('hidden');"
#detailsJSend = "});\n';"

		# do substitutions here
		if index == 1 and response == 200:
			page = replace(page, "$title$", self.server.httpoutput.title)
			page = replace(page, "$about$", self.server.httpoutput.about)
			page = replace(page, "$time$", self.server.httpoutput.lastUpdate)
			# sort out the sensor stuff
			table = ''
			details = ''
			sensors = 0
			for i in self.server.httpoutput.data:
				line = replace(self.server.httpoutput.tableRow, "$sensorName$", i["name"])
				line = replace(line, "$reading$", str(i["value"]))
				line = replace(line, "$units$", i["symbol"])
				line = replace(line, "$sensorId$", str(sensors))
				table += line
				line = replace(self.server.httpoutput.sensorDetails, "$sensorId$", str(sensors))
				line = replace(line, "$sensorName$", i["name"])
				line = replace(line, "$sensorText$", "Sensor description.")
				details += line
				sensors += 1
			page = replace(page, "$table$", table)
			page = replace(page, "$details$", details)
			# sort out the javascript for the sensors now
			javascript = ''
			for i in range(0, sensors):
				line = replace(self.server.httpoutput.detailsJSstart, "$sensorId$", str(i))
				line += replace(self.server.httpoutput.detailsJSshow, "$sensorId$", str(i))
				# hide every other
				for j in range(0, sensors):
					if i != j:
						line += replace(self.server.httpoutput.detailsJShide, "$sensorId$", str(j))
				javascript += line + self.server.httpoutput.detailsJSend;
			page = replace(page, "$javascript$", javascript)

		self.send_response(response)
		if response == 200:
			fileName, fileExtension = os.path.splitext(toread)
			if fileExtension == '.png':
				self.send_header("Content-Type", "image/png")
			elif fileExtension == '.css':
				self.send_header("Content-Type", "text/css")
			elif fileExtension == '.js':
				self.send_header("Content-Type", "application/javascript")
			else:
				self.send_header("Content-Type", "text/html")
		else:
			self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", len(page))
		self.end_headers()
		self.wfile.write(page)
		self.wfile.close()
