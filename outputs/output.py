"""Generic Output plugin description (abstract) for sub-classing.

A generic description of an Output plugin, which can then be sub-classed
for specific Outputs. This is an abstract base class (ABC) and so cannot
be instantiated directly.

"""
from abc import ABCMeta, abstractmethod
import socket
import ConfigParser
import os

class Output(object):
    """Generic Output plugin description (abstract) for sub-classing.

    A generic description of an Output plugin, which can then be sub-classed
    for specific Outputs. This is an abstract base class (ABC) and so cannot
    be instantiated directly.

    """

    __metaclass__ = ABCMeta
    requiredGenericParams = ["target"]
    optionalGenericParams = ["calibration", "metadata", "limits", "support"]
    requiredSpecificParams = None
    optionalSpecificParams = None
    commonParams = None

    def __init__(self, config):
        self.name = type(self).__name__
        #TODO: Is self.async really required?
        self.async = False
        self.params = {}
        if self.setallparams(config):
            if (self.params["target"] == "internet") and not self.check_conn():
                msg = "Skipping output plugin " + self.name
                msg += " because no internet connectivity."
                #msg = format_msg(msg, 'error')
                print(msg)
                #logthis("info", msg)
                raise NoInternetConnection
        else:
            msg = "Failed to set parameters for output plugin " + self.name
            print(msg)
            #logthis("error", msg)
 
    def setallparams(self, OUTPUTCONFIG):
        """
 
        Check that 'params' used to init the object contains the required
        parameters; raise an error if not. Then check whether it contains
        any of the optional parameters; set them to False if not.
        This is done for both the 'generic' parameters which apply to all
        subclasses of this Output object, and for 'specific' parameters
        which are defined for individual subclasses.

        """
        if self.name in OUTPUTCONFIG.sections():
            self.extractparams(OUTPUTCONFIG, self.requiredGenericParams, "required")
            self.extractparams(OUTPUTCONFIG, self.requiredSpecificParams, "required")
            self.extractparams(OUTPUTCONFIG, self.optionalGenericParams, "optional")
            self.extractparams(OUTPUTCONFIG, self.optionalSpecificParams, "optional")
            return True
        else:
            msg = "Missing config section for plugin " + self.name + "."
            print(msg)
            msg += "This should be found in file: " + filetocheck
            #msg = format_msg(msg, 'error')
            print(msg)
            raise MissingSection
        return False

    def extractparams(self, config, paramset, kind):
        if paramset is not None:
            extracted = {}
            for param in paramset:
                if config.has_option(self.name, param):
                    extracted[param] = self.sanitiseparam(config.get(self.name, param))
                else:
                    if kind == "required":
                        msg = "Missing required parameter '" + param
                        msg += "' for plugin " + self.name + "."
                        print(msg)
                        msg += "This should be found in the outputs.cfg file."
                        #msg = format_msg(msg, 'error')
                        print(msg)
                        raise MissingParameter 
                    else:
                        msg = "Missing optional parameter '" + param 
                        msg += "' for plugin " + self.name + ". Setting to False."
                        #msg = format_msg(msg, 'info')
                        #logthis(msg)
                        extracted[param] = False
            self.params.update(extracted)

    @staticmethod
    def sanitiseparam(value):
        # Always test for bool first: http://www.peterbe.com/plog/bool-is-int
        if isinstance(value, bool):
            return value
        if value.lower() in ["on", "yes", "true", "1"]:
            return True
        if value.lower() in ["off", "no", "false", "0"]:
            return False
        return value

    @abstractmethod
    def output_data(self):
        """Output data.

        Output data in the format stipulated by this plugin.
        Even if it is not appropriate for the plugin to output data
        (e.g. for support plugins), this method is required because
        airpi.py looks for it in when setting up plugins; this is why it
        is abstract.

        The standard method signature would be:
        output_data(self, data, sampletime)
        where...
        - 'data' is a dict containing the data to be output, usually
           called 'datapoints'.
        - 'sampletime' is a datetime representing the time the sample
           was taken.

        In situations where the sub-class defines a support plugin (e.g.
        "calibration") the sub-class may not actually be able/designed
        to ouptput data; in such circumstances the method should just
        return True. In those cases, the method signature can have a
        single 'self' argument as shown above.

        See the docstrings for individual methods within sub-classes for
        more detail on specific cases.

        Args:
            self: self.

        """
        pass

    def output_metadata(self, metadata = None):
        """Output metadata.

        Output metadata in the format stipulated by this plugin.
        Even if it is not appropriate for the plugin to output metadata
        (e.g. for support plugins), this method is required because
        airpi.py looks for it in when setting up plugins; this is why it
        is abstract.

        In situations where the sub-class defines a support plugin (e.g.
        "calibration") the sub-class may not actually be able/designed
        to ouptput data; in such circumstances the method should just
        return True. In those cases, the method signature can have a
        single 'self' argument as shown above;  the 'metadata' argument 
        is never used.

        See the docstrings for individual methods within sub-classes for
        more detail on specific cases.

        Args:
            self: self.
            metadata: Dict containing the metadata to be output.

        """
        return True

    @staticmethod
    def gethostname():
        """Get current hostname.

        Get the current hostname of the Raspberry Pi.

        Returns:
            string The hostname.

        """
        if socket.gethostname().find('.') >= 0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]
        return host

    def getname(self):
        """Get Class name.

        Get the name of the class. Lots of output Classes inherit from
        Output, so this varies depending on which one we're looking at.

        Returns:
            string The class name.

        """
        return self.__class__.__name__

class MissingParameter(Exception):
    """Exception to raise when the outputs.cfg file is missing a required
    parameter.

    """
    pass

class MissingSection(Exception):
    """ Exception to raise when there is no section for the plugin in
    the outputs.cfg config file.

    """
    pass

class NoInternetConnection(Exception):
    """ Exceeption to raise when there is no internet connectivity.

    """
    pass
