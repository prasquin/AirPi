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

    def output_data(self, dataPoints):
        #TODO: Include GPS location data in this output
        """Output data.

        Output data in the format stipulated by the plugin. Calibration is
        carried out first if required.
        Note this method does not yet output GPS (Location) data.

        Args:
            self: self.
            dataPoints: A dict containing the data to be output.

        """
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        arr ={} 
        counter = 1
        for point in dataPoints:
            if point["name"] != "Location":
                if point["value"] != None: #this means it has no data to upload.
                    arr["field" + str(counter)] = round(point["value"],2)
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
        """Output metadata.

        Output metadata for the run in the format stipulated by this plugin.
        Metadata is set in airpi.py and then passed as a dict to each plugin
        which wants to output it. Even if it is not appropriate for the output
        plugin to output metadata, this method is required because airpi.py
        looks for it in its own output_metadata() method. In such cases, this
        method will simply return boolean True.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        return True