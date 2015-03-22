import output
import requests
import calibration

class Thingspeak(output.Output):
    requiredParams = ["apikey", "needsinternet"]
    optionalParams = ["calibration"]

    def __init__(self, params):
        self.apikey = params["apikey"]
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.cal.checkcal(params)

    def output_data(self, datapoints, dummy):
        #TODO: Include GPS location data in this output
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Note this method does not yet output GPS (Location) data.
        Because this particular plugin (plot) does not show time, the
        third argument (normally called 'sampletime') is called 'dummy'
        to facilitate compliance with pylint.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.
            dummy: datetime representing the time the sample was taken.

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)
        arr = {}
        counter = 1
        for point in datapoints:
            if point["name"] != "Location":
                if point["value"] != None: #this means it has no data to upload.
                    arr["field" + str(counter)] = round(point["value"], 2)
                counter += 1
        url = "https://api.thingspeak.com/update?key=" + self.apikey
        try:
            z = requests.post(url, params=arr)
            if z.text == "0":
                print("Error: ThingSpeak error - " + z.text)
                print("Error: ThingSpeak URL  - " + z.url)
                return False
        except Exception:
            return False
        return True

    def output_metadata(self):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. This particular plugin cannot output metadata, so this
        method will always return True. This is an abstract method of
        the Output class, which this class inherits from; this means you
        shouldn't (and can't) remove this method. See docs in the Output
        class for more info.

        Args:
            self: self.

        Returns:
            boolean True in all cases.
        """
        return True
