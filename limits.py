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

class Limits(object):
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

    def __init__(self, params):
        """Initialise.

        Initialise the Limits class, using the parameters passed in
        'params'. Note that the 'requiredParams' and 'optionalParams'

        Args:
            self: self.
            params: Parameters to be used as the limits. Can be empty. If not, must be
                    a list of phenomena names with corresponding strings containing
                    comma-separated value and unit, e.g.:
                    params["nitrogen_dioxide"] = ["10,Ohms"]
                    params["carbon_monoxide"] = ["20",ppm"]

        """
        temp = dict((k.lower(), v) for k,v in params.iteritems())
        self.limits = {}
        for name, detail in temp.iteritems():
            self.limits[name] = {}
            self.limits[name]["value"] = float(detail[0])
            self.limits[name]["unit"] = detail[1]


    def isbreach(self, samplename, samplevalue, sampleunit):
        """Check whether a data point breaches a limit.

        Checks whether the value of a specific data point breaches the
        defined limit.
        NOTE: We are comparing instantaneous AirPi values with, in some
        cases, EU limits per hourly average, calendar year (NO2) or
        eight-hour average (CO).

        Args:
            self: self.
            datapoint: The datapoint to be tested. Passed by the output
                       plugin which is checking for the breach.

        """
        samplename = samplename.lower()
        if samplename in self.limits:
            if samplevalue > float(self.limits[samplename]["value"]):
                if sampleunit == self.limits[samplename]["unit"]:
                    return True
                else:
                    print("ERROR: Limit units do not match measurement units for " + samplename)
                    print("       " + sampleunit + " is not the same as " + self.limits[samplename]["unit"])
        return False