"""Generic Support plugin description (abstract) for sub-classing.

A generic description of a Support plugin, which can then be sub-classed
for specific Supports. This is an abstract base class (ABC) and so cannot
be instantiated directly.

"""
from abc import ABCMeta, abstractmethod
import ConfigParser
import os

class Support(object):
    """Generic Support plugin description (abstract) for sub-classing.

    A generic description of a Support plugin, which can then be sub-classed
    for specific Supports. This is an abstract base class (ABC) and so cannot
    be instantiated directly.
    Note that Support plugins do not currently have any generic params,
    nor do they check for internet connectivity.

    """

    __metaclass__ = ABCMeta
    requiredSpecificParams = None
    optionalSpecificParams = None

    def __init__(self, config):
        self.name = type(self).__name__
        #TODO: Is self.async really required?
        self.async = False
        self.params = {}
        if not self.setallparams(config):
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
            self.extractparams(OUTPUTCONFIG, self.requiredSpecificParams, "required")
            self.extractparams(OUTPUTCONFIG, self.optionalSpecificParams, "optional")
            return True
        else:
            msg = "Missing config section for plugin " + self.name + "."
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
