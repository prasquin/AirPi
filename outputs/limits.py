"""A module to define exposure limits.

A support module which is used to define exposure limits for gases.
Once defined, the Class is shared across all objects which
access it, i.e. limits are the same across all output plugins
which apply them. All limits are classed as 'breached' if the
current concentration of gas goes *above* the defined level.

Where EU limits are defined as averages over time, e.g. average CO level
over eight hours, we are only comparing instantaneous values from the
AirPi to them, so this is not entirely accurate (close enough though!).

"""

import output

class Limits(output.Output):
    """A module to define exposure limits.

    A support module which is used to define exposure limits for gases.
    Once defined, the Class is shared across all objects which
    access it, i.e. limits are the same across all output plugins
    which apply them. All limits are classed as 'breached' if the
    current concentration of gas goes *above* the defined level.

    Where EU limits are defined as averages over time, e.g. average CO level
    over eight hours, we are only comparing instantaneous values from the
    AirPi to them, so this is not entirely accurate (close enough though!).

    """

    requiredParams = []
    optionalParams = []

    def __init__(self, params):
        """Initialise.

        Initialise the Limits class, using the parameters passed in
        'params'. Note that the 'requiredParams' and 'optionalParams'
        are used to check that 'params' contains the appropriate
        options (this happens in define_plugin_params() in airpi.py
        after this object has been created).
        TODO: Move that functionality to the output.py module and let
              output plugins inherit it.

        Args:
            self: self.
            params: Parameters to be used in the initialisation.

        """
        for element in ["enabled", "support", "filename"]:
            if element in params:
                del params[element]
        self.limits = params

    def isbreach(self, datapoint):
        """Check whether a data point breaches a limit.

        Checks whether the value of a specific data point breaches the
        defined limit.
        NOTE: We are comparing instantaneous AirPi values with, in some
        cases, EU limits per hourly average, calendar year (NO2) or
        eight-hour average (CO).

        The 'measures' list below could be extended to include other
        measures; in this case the FIRST element in the array should be
        what matches the reference throughout the rest of this module
        (e.g. "co" is first in the array and matches self.limit["co"]
        and self.unit["co"]. It wouldn't work if we used "co" 1st below
        and then self.limit["carbmono"]).

        Args:
            self: self.
            datapoint: The datapoint to be tested. Passed by the output
                       plugin which is checking for the breach.

        """
        for measure, detail in self.limits.iteritems():
            if datapoint["name"].lower() == measure:
                [value, units] = detail.split(',', 1)
                if datapoint["value"] > float(value):
                    if datapoint["unit"] == units:
                        return True
                    else:
                        print("ERROR: Limit units do not match measurement units for " + datapoint["name"])
                        print("       " + datapoint["unit"] + " is not the same as " + units)
        return False

    @staticmethod
    def output_metadata(metadata):
        """Output metadata.

        Output metadata for the run in the format stipulated by this
        plugin. This particular plugin cannot output metadata, so this
        method will always return True. This is an abstract method of
        the Output class, which this class inherits from; this means you
        shouldn't (and can't) remove this method. See docs in the Output
        class for more info.

        Args:
            metadata: Dict containing the metadata to be output.

        Returns:
            boolean True in all cases.
        """
        return True

    @staticmethod
    def output_data(self, dummy_a, dummy_b):
        """Output data.

        Output data in the format stipulated by the plugin. Even if it
        is not appropriate for the plugin to output data (e.g. for
        support plugins), this method is required because airpi.py
        looks for it in when setting up plugins. In such cases, arguments
        will be named 'dummy' to facilitate compliance with pylint, and
        this method will simply return boolean True.

        Args:
            self: self.
            dummy_a: A dict containing the data to be output.
            dummy_b: datetime representing the time the sample was taken.

        Returns:
            boolean True in all cases (for this partiular plugin).

        """
        return True
