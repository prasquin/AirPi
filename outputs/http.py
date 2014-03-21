import output
import os
from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
import datetime

# useful resources:
# http://unixunique.blogspot.co.uk/2011/06/simple-python-http-web-server.html
# http://docs.python.org/2/library/simplehttpserver.html
# http://stackoverflow.com/questions/10607621/a-simple-website-with-python-using-simplehttpserver-and-socketserver-how-to-onl
# http://www.huyng.com/posts/modifying-python-simplehttpserver/
# http://stackoverflow.com/questions/6391280/simplehttprequesthandler-override-do-get

class HTTP(output.Output):
	requiredData = ["wwwPath"]
	optionalData = ["port", "history", "name", "about"]

	def __init__(self,data):
		self.www = data["wwwPath"]
		if "port" in data:
			self.port = int(data["port"])
		else:
			self.port = 8080
		if "history" in data:
			if data["history"].lower in ["on","true","1","yes"]:
				self.history = 1
			else:
				self.history = 0
		else:
			self.history = 0
		if "name" in data:
			self.name = data["name"]
		else:
			self.name = "AirPi"
		if "about" in data:
			self.about = data["about"]
		else:
			self.about = "An AirPi weather station."

		handler = requestHandler
		self.server = SocketServer.TCPServer(("",self.port), handler)
		self.server.serve_forever()

	def outputData(self,dataPoints):
		self.data = dataPoints
		self.lastUpdate = str(datetime.datetime.now())
		return True

class requestHandler(SimpleHTTPRequestHandler):

	def do_GET(self):
		if self.path == '/' or self.path == 'index.html'
			self.path = 'index.html'
			index = 1
		else
			index = 0

		toread = self.www + os.sep + self.path
		if os.path.isffile(toread):
			pageFile = open(toread, 'r')
			page = pageFile.read()
			pageFile.close()
			response = 200
		else:
			page = "quoth the raven, 404"
			response = 404

		if index = 1 and response = 200:
			pass # do substitutions here

		self.send_response(response)
		self.send_header("Content-Type", "text/html")
		self.send_header("Content-length", len(page))
		self.end_headers()
		self.wfile.write(page)
		self.wfile.close()
