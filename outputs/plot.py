"""A module to print AirPi data to screen as a graph.

A module which is used to output data from an AirPi onto screen (or more
accurately, stdout) in a simple ASCII graph format. This will not
include GPS data.

"""

import os
import output
import calibration
import ap

class Plot(output.Output):
    """A module to print AirPi data to screen as a graph.

    A module which is used to output data from an AirPi onto screen (or
    more accurately, stdout). This can include GPS data if present,
    along with metadata (again, if present).

    """

    requiredParams = ["target", "metric"]
    optionalParams = ["calibration"]

    def __init__(self, params):
        self.cal = calibration.Calibration.sharedClass
        self.docal = self.checkcal(params)
        self.target = params["target"]
        self.history = []
        self.metric = params["metric"]
        self.unit = None

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

    def output_data(self, datapoints, dummy):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present
        a dict containing one value and associated properties such as
        units and symbols, while the latter presents a dict containing
        several readings such as latitude, longitude and altitude, but
        no units or symbols.
        Because this particular plugin (plot) does not show time, the
        third argument (normally called 'sampletime') is called 'dummy'
        to facilitate compliance with pylint.

        Args:
            self: self.
            datapoints: A dict containing the data to be output.

        Returns:
            boolean True if data successfully printed to stdout.

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)

        for point in datapoints:
            if point["name"] == self.metric:
                self.history.append(int(point["value"]))
                if self.unit is None:
                    self.unit = point["unit"]

        x = range(0, len(self.history))
        y = self.history
        xlimits = [min(x), max(x)]
        ylimits = [min(self.history)-(0.11*min(self.history)), max(self.history)+(0.1*max(self.history))]
        p = ap.AFigure(margins=(0, 0), xlim=xlimits, ylim=ylimits)
        _ = p.plot(x, y, marker='_o', plot_slope=True)
        os.system("clear")
        print("[AirPi] Plotting " + self.metric + " (" + self.unit + "):" + os.linesep)
        print(p.plot(x, y, marker='_s'))
        return True
