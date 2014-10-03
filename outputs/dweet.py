import output
import calibration
import requests

class Dweet(output.Output):
    requiredParams = ["needsinternet"]
    optionalParams = ["calibration", "thing"]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
        self.thing = params["thing"]
        if "<hostname>" in self.thing:
            self.thing = self.thing.replace("<hostname>", self.getHostname())

    def output_data(self, dataPoints):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration is
        carried out first if required.
        Note this method does not output GPS (Location) data, as dweet has no
        way of visualising it.

        Args:
            self: self.
            dataPoints: A dict containing the data to be output.

        """
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        data = {}
        for point in dataPoints:
            if point["name"] != "Location":
                data[point["name"].replace(" ", "_")] = round(point["value"], 2)
        try:
            z = requests.get("https://dweet.io/dweet/for/" + self.thing, params=data)
            response = z.json()
            if "succeeded" not in response['this']: 
                print("Error: dweet.io error - " + z.text)
                print("Error: dweet.io URL  - " + z.url)
                return False
        except Exception:
            print("Error: Failed to dweet")
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

    def get_url(self):
        return "https://dweet.io/follow/" + self.thing 