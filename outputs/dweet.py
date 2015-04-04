"""A module to output data to dweet.

A module which is used to output data from an AirPi to the 'dweet'
service at http://dweet.io  This does not include GPS data or metadata,
because dweet has no way of representing those data.

Note that this module does not output metadata (dweet has no way of
representing it), so the output_metadata() method is inherited from the
parent class (Output), i.e. always returns True.

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

    requiredParams = ["target", "needsinternet"]
    optionalParams = ["calibration", "thing"]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkcal(params)
        self.target = params["target"]
        self.thing = params["thing"]
        if "<hostname>" in self.thing:
            self.thing = self.thing.replace("<hostname>", self.gethostname())

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
        req = None
        for point in datapoints:
            if point["name"] != "Location":
                data[point["name"].replace(" ", "_")] = round(point["value"],
                                                                2)
        try:
            req = requests.get("https://dweet.io/dweet/for/" + self.thing,
                                params=data)
        except Exception as e:
            print("ERROR: Failed to contact the dweet service.")
            print("ERROR: " + str(e))
            return False
        response = req.json()
        if "succeeded" not in response['this']:
            print("ERROR: dweet.io responded with an error - " + req.text)
            print("ERROR: dweet.io URL  - " + req.url)
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

    def get_help(self):
        """Get help for this plugin.

        Where help is available for this plugin, get it.

        Returns:
            string The help.

        """
        return "Dweet: Data are Dweeting to " + self.get_url()
