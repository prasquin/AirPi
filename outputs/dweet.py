"""A module to output data to dweet.

A module which is used to output data from an AirPi to the 'dweet'
service at http://dweet.io  This does not include GPS data or metadata,
because dweet has no way of representing those data.

"""

import output
import calibration
import requests

class Dweet(output.Output):
    """A module to output data to dweet.

    A module which is used to output data from an AirPi to the 'dweet'
    service at http://dweet.io  This does not include GPS data or metadata,
    because dweet has no way of representing those data.

    """

    requiredParams = ["needsinternet"]
    optionalParams = ["calibration", "thing"]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkCal(params)
        self.thing = params["thing"]
        if "<hostname>" in self.thing:
            self.thing = self.thing.replace("<hostname>", self.getHostname())

    def output_data(self, datapoints):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Note this method does not output GPS (Location) data, as dweet
        has no way of visualising it.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.

        Returns:
            boolean True if data successfully output to dweet; False if
                not

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)
        data = {}
        for point in datapoints:
            if point["name"] != "Location":
                data[point["name"].replace(" ", "_")] = round(point["value"],
                                                                2)
        try:
            req = requests.get("https://dweet.io/dweet/for/" + self.thing,
                                params=data)
            response = req.json()
            if "succeeded" not in response['this']: 
                print("Error: dweet.io error - " + req.text)
                print("Error: dweet.io URL  - " + req.url)
                return False
        except Exception:
            print("Error: Failed to dweet")
            return False
        return True

    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it. Even if it is not
        appropriate for the output plugin to output metadata, this
        method is required because airpi.py looks for it in its own
        output_metadata() method. In such cases, this method will simply
        return boolean True.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        Returns:
            boolean True in all cases.

        """
        return True

    def get_url(self):
        """Get the dweet.io URL for this AirPi.

        Get the dweet.io URL where data output for this AirPi can be
        viewed.
        See the note in airpi.py about replacing this with something
        more elegant.

        Args:
            self: self.

        Returns:
            The dweet.io URL.

        """
        return "https://dweet.io/follow/" + self.thing 