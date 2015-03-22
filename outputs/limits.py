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

    requiredParams = ["limitno2", "limitco"]
    optionalParams = ["unitno2", "unitco"]

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
        self.limits = {}

        #if "unitno2" not in params:
        #    params["unitno2"] = None
        #if "unitco" not in params:
        #    params["unitco"] = None

        self.setno2limit(params["limitno2"], params["unitno2"])
        self.setcolimit(params["limitco"], params["unitco"])

    def setno2limit(self, limit, unit = None):
        """Set the NO2 limit.

        Set the upper limit for NO2 concentration, above which is
        considered a breach. The 'limit' argument can be one of the
        predefined names (in which case this function converts that to the
        appropriate value) or an integer or float, in which case the
        value will be used as the breach limit in whatever 'unit' is.

        EU limits are given in ug/m^3:
        http://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=OJ:L:2008:152:0001:0044:EN:PDF

        ppm values have been derived from these as follows:

        Molar volume of any gas (from the Ideal Gas Law): V = (nRT)/P
            n = Number of Moles = 1
            R = ideal gas constant = 0,8206
            T (in Leicester, UK) = ~9.85 oC average over a year = 282.845833316 K
            P = 1.013 ATM
            So V = (nRT)/P = (1*0.08205736*282.845833316)/1.013 = 22.91172988 L

        Molecular mass of NO2 = 46.0055
        1 ppb    = MolecularMass/MolarVolume = 46.0055/22.91172988 = 2.007945286 ug/m^3
        1 ug/m^3 = 0.515982846 ppb

        See also:
        http://uk-air.defra.gov.uk/assets/documents/reports/cat06/0502160851_Conversion_Factors_Between_ppb_and.pdf

        Args:
            limit: The limit to be applied. The name of a pre-defined
                   limit, or a float for a custom limit.
            unit: The units in which a custom 'limit' is measured. {ppm|Ohms}

        """
        self.limits["no2"] = {}
        self.limits["no2"]["names"] = ["no2", "nitrogen dioxide", "nitrogen_dioxide", "nitrogen-dioxide"]
        if self.is_number(limit):
            if unit is None:
                print("ERROR: Unable to set custom NO2 limit because Unit is missing from cfg file.")
                return False
            else:
                self.limits["no2"]["kind"] = "custom"
                self.limits["no2"]["unit"] =  unit
	        self.limits["no2"]["value"] = limit
        else:
            self.limits["no2"]["kind"] = "preset"
	    self.limits["no2"]["unit"] = "ppm"
            if limit == "EU-hourly":
                self.limits["no2"]["value"] = 103.1965692 #  200 ug/m^3
            elif limit == "EU-yearly":
                self.limits["no2"]["value"] = 20.63931384 #   40 ug/m^3
            else:
                print("ERROR: Unknown NO2 limit specified. Use preset name or a custom number.")
                return False
        return True

    def setcolimit(self, limit, unit = None):
        """Set the CO limit.

        Set the upper limit for CO concentration, in ppm, above which
        is considered a breach. The 'limit' argument can be one of the
        predefined names, in which case this function converts that to the
        appropriate ppm value, or an integer or float, in which case the
        value will be used as the breach limit in ppm.

        EU limits are given in ug/m^3:
        http://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=OJ:L:2008:152:0001:0044:EN:PDF

        ppm value has been derived from these as follows:

        Molar volume of any gas (from the Ideal Gas Law): V = (nRT)/P
            n = Number of Moles = 1
            R = ideal gas constant = 0,8206
            T (in Leicester, UK) = ~9.85 oC average over a year = 282.845833316 K
            P = 1.013 ATM
            So V = (nRT)/P = (1*0.08205736*282.845833316)/1.013 = 22.91172988 L

        Molecular mass of CO = 28.01
        1 ppb    = MolecularMass/MolarVolume = 28.01/22.91172988 = 1.222517904 ug/m^3
        1 ug/m^3 = 0.81798393 ppb

        See also:
        http://uk-air.defra.gov.uk/assets/documents/reports/cat06/0502160851_Conversion_Factors_Between_ppb_and.pdf

        Args:
            limit: The limit to be applied. The name of a predefined
                   limit, or a float for a custom limit.
            unit: The units in which a custom limit is measured. {ppm|Ohms}

        """
        self.limits["co"] = {}
        self.limits["co"]["names"] = ["co", "carbon monoxide", "carbon_monoxide", "carbon-monoxide"]
        if self.is_number(limit):
            if unit is None:
                print("ERROR: Unable to set custom CO limit because Unit is missing from cfg file.")
                return False
            else:
                self.limits["co"]["kind"] = "custom"
                self.limits["co"]["unit"] = unit
                self.limits["co"]["value"] = limit
        else:
            if limit == "EU":
                self.limits["co"]["kind"] = "preset"
                self.limits["co"]["unit"] = "ppm"
                self.limits["co"]["value"] = 8179.8393 #  10 mg/m^3
            else:
                print("ERROR: Unknown CO limit specified. Use preset name or a custom number.")
                return False
        return True


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
        for measure in [self.limits["no2"]["names"], self.limits["co"]["names"]]:
            if datapoint["name"].lower() in measure:
                if datapoint["value"] > float(self.limits[measure[0]]["value"]):
                    if datapoint["unit"] == self.limits[measure[0]]["unit"]:
                        return True
                    else:
                        print("ERROR: Limit units do not match measurement units for " + datapoint["name"])
                        print("       " + datapoint["unit"] + " is not the same as " + self.limits[measure]["unit"])
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
    def is_number(tocheck):
        """Does a string represent a number?

        Does a string represent a number? Pulled from here because there
        is nothing built in to Python to do this!
        http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-in-python

        Args:
            tocheck: String to check

        Returns:
            boolean True if the string represents a number

        """
        try:
            float(tocheck)
            return True
        except ValueError:
            return False


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
