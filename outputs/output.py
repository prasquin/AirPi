import time
import socket

class Output(object):
    def __init__(self, params):
        raise NotImplementedError

    def output_data(self, dataPoints, sampletime):
        """Output data.

        Output data in the format stipulated by the plugin. Calibration is
        carried out first if required.
        Note this method takes account of the different data formats for
        'standard' sensors as distinct from the GPS. The former present a dict
        containing one value and associated properties such as units and
        symbols, while the latter presents a dict containing several readings
        such as latitude, longitude and altitude, but no units or symbols.

        Args:
            self: self.
            dataPoints: A dict containing the data to be output.
            sampletime: datetime representing the time the sample was taken.

        """
        raise NotImplementedError

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
        raise NotImplementedError

    def checkCal(self, params):
        """Check whether calibration has been requested.

        Check whether calibration of raw data has been requested for this output
        plugin. This will have been done in airpi.py as part of set_up_outputs()
        - more specifically, by define_plugin_params(). This method does not
        actually carry out any calibration; it just records whether or not it
        *should* be done.

        Args:
            self: self.
            params: dict The setup parameters for the run.

        """
        doCal = 0;
        if "calibration" in params:
            if params["calibration"].lower() in ["on", "yes", "true", "1"]:
                doCal = 1
        return doCal

    def getHostname(self):
        """Get current hostname.

        Get the current hostname of the Raspberry Pi.

        Returns:
            string The hostname.

        """
        if socket.gethostname().find('.')>=0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]
        return host

    def get_name(self):
        """Get Class name.

        Get the name of the class. Lots of output Classes inherit from
        Output, so this varies depending on which one we're looking at.

        Returns:
            string The class name.

        """
        return self.__class__.__name__
