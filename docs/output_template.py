"""A template AirPi output plugin.

This file is a basic template which can be used as a base when creating
a custom AirPi output plugin. You should change the variable names and
function definitions as required, and also add plugin details to the file 
cfg/outputs.cfg"""

# All output plugins are sub-classes of output.
# calibration should be supported by all output plugins.
import output
import calibration

class MyOutputClass(output.Output):
    """A class to output AirPi data somewhere.

    A class which is used to output data from an AirPi into a
    particular format.

    """

    # Parameters listed in requiredParams *MUST* be defined in outputs.cfg
    # Parameters listed in optionalParams can be defined in outputs.cfg if
    # appropriate, but are optional.
    requiredParams = ["outputDir", "outputFile"]
    optionalParams = ["calibration", "metadatareqd"]

    def __init__(self, params):
        """
        Initialisation.

        Any initialisation code goes here.
        """


    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. Metadata is set in airpi.py and then passed as a dict to
        each plugin which wants to output it.

        Args:
            self: self.
            metadata: dict The metadata for the run.

        """
        if self.metadatareqd:
            # Output the metadata somehow.

    def output_data(self, datapoints):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration
        is carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present
        a dict containing one value and associated properties such as
        units and symbols, while the latter presents a dict containing
        several readings such as latitude, longitude and altitude, but
        no units or symbols.
        Remember, one JSON object is output per datapoint, so the file
        will contain lots of them (which isn't valid JSON).

        Args:
            self: self.
            datapoints: A dict containing the data to be output.

        Returns:
            boolean True if data successfully written to file.

        """
        if self.docal == 1:
            datapoints = self.cal.calibrate(datapoints)

        # Output the actual data here.
        
        # Return True once we've output all of the data.
        return True

    def __del__(self):
        """ Any exit code, e.g. ensuring files are closed. """