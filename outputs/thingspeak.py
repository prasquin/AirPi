import output
import requests
import calibration

class Thingspeak(output.Output):
    requiredParams = ["APIKey", "needsinternet"]
    optionalParams = ["calibration"]

    def __init__(self, params):
        self.APIKey=params["APIKey"]
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)

# TODO: See if this can use requests instead of urllib and httplib
    def output_data(self, dataPoints):
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        arr ={} 
        counter = 1
        for i in dataPoints:
            if i["value"] != None: #this means it has no data to upload.
                arr["field" + str(counter)] = round(i["value"],2)
            counter += 1
        url = "https://api.thingspeak.com/update?key=" + self.APIKey
        print(url)
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        try:
            z = requests.post(url, params=arr)
            if z.text == "0": 
                print "Error: ThingSpeak error - " + z.text
                print "Error: ThingSpeak URL  - " + z.url
                return False
        except Exception:
            return False
        return True

    def output_metadata(self, metadata):
        return True