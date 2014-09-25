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
        if self.docal == 1:
            dataPoints = self.cal.calibrate(dataPoints)
        data = {}
        for i in dataPoints:
            data[i["name"].replace(" ", "_")] = round(i["value"], 2)
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
        return True

    def get_url(self):
        return "https://dweet.io/follow/" + self.thing 