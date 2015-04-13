"""Generic Output plugin description (abstract) for sub-classing.

A generic description of an Output plugin, which can then be sub-classed
for specific Outputs. This is an abstract base class (ABC) and so cannot
be instantiated directly.

"""
from abc import ABCMeta, abstractmethod
import socket

class Output(object):
    """Generic Output plugin description (abstract) for sub-classing.

    A generic description of an Output plugin, which can then be sub-classed
    for specific Outputs. This is an abstract base class (ABC) and so cannot
    be instantiated directly.

    """

    __metaclass__ = ABCMeta
    requiredGenericParams = ["target"]
    optionalGenericParams = ["calibration", "metadata", "limits"]
    requiredSpecificParams = None
    optionalSpecificParams = None
    commonParams = None

    def __init__(self, params):
        self.name = type(self).__name__
        #TODO: Enable this
        #config = self.check_cfg_file(filetocheck)
        #self.doparams = {}
        #if self.doparams(config)
        self.dolimits = self.checklimits(params)
        self.dometadata = self.checkmetadata(params)
        self.cal = self.checkcal(params)
        self.target = params["target"]
        #else:
        #    # doparams failed so we can actually delete these two lines
 
    def doparams(OUTPUTCONFIG):
        """
 
        Check that 'params' used to init the object contains the required
        parameters; raise an error if not. Then check whether it contains
        any of the optional parameters; set them to False if not.
        This is done for both the 'generic' parameters which apply to all
        subclasses of this Output object, and for 'specific' parameters
        which are defined for individual subclasses.

        """
        #TODO: Actually use this function instead of airpi.py
        if self.name in OUTPUTCONFIG.sections():
            for paramset in ["requiredGenericParams", "requiredSpecificParams"]:
                for reqdparam in paramset:
                    if OUTPUTCONFIG.has_option(self.name, reqdparam):
                        self.params[reqdparam] = self.sanitiseparam(OUTPUTCONFIG.get(name, reqdparam))
                    else:
                        msg = "Missing required parameter '" + reqdparam
                        msg += "' for plugin " + self.name + "."
                        print(msg)
                        msg += "This should be found in file: " + filetocheck
                        msg = format_msg(msg, 'error')
                        print(msg)
                        raise MissingParameter
            for paramset in ["optionalGenericParams", "optionalSpecificParams"]:
                for optparam in paramset:
                    if OUTPUTCONFIG.has_option(name, optparam):
                        self.params[optparam] = self.sanitiseparam(OUTPUTCONFIG.get(name, optparam))
                    else:
                        msg = "Missing optional parameter '" + optparam 
                        msg += "' for plugin " + self.name + ". Setting to False."
                        msg = format_msg(msg, 'info')
                        print(msg)
                        self.params[optparam] = False
            return True
        else:
            msg = "Missing config section for plugin " + self.name + "."
            print(msg)
            msg += "This should be found in file: " + filetocheck
            msg = format_msg(msg, 'error')
            print(msg)
            raise MissingSection

    def sanitiseparam(value):
        # Test for bool first: http://www.peterbe.com/plog/bool-is-int
        if isinstance(value, bool):
            return value
        if value.lower() in ["on", "yes", "true", "1"]:
            return True
        if value.lower() in ["off", "no", "false", "0"]:
            return False
        return value


    @staticmethod
    def check_cfg_file(filetocheck):
        """Check cfg file exists.

        Check whether a specified cfg file exists. Print and log a warning
        if not. Log the file name if it does exist.

        Args:
            filetocheck: The file to check the existence of.

        Returns:
            boolean True if the file exists.

        """
        if not os.path.isfile(filetocheck):
            msg = "Unable to access config file: " + filetocheck
            print(msg)
            LOGGER.error(msg)
            exit(1)
        else:
            msg = "Config file: " + filetocheck
            LOGGER.info(msg)
            outputconfig = ConfigParser.SafeConfigParser()
            outputconfig.read(filetocheck)
            return outputconfig

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

    def output_metadata(self, metadata = False):
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
    def checkcal(params):
        """Check whether calibration has been requested.

        Check whether calibration of raw data has been requested for this output
        plugin. This will have been done in airpi.py as part of set_up_outputs()
        - more specifically, by define_plugin_params(). This method does not
        actually carry out any calibration; it just records whether or not it
        *should* be done.

        Args:
            params: dict The setup parameters for the run.

        Returns:
            calibration object if calibration is requested. False if not.
        """
        if "calibration" in params:
            if isinstance(params["calibration"], bool):
                return params["calibration"]
            if params["calibration"].lower() in ["on", "yes", "true", "1"]:
                return calibration.Calibration.sharedClass
        return False


    @staticmethod
    def checklimits(params):
        """Check whether limits have been requested.

        Check whether breach detection using the limits function has been
        requested for this output plugin.

        Args:
            params: dict The setup parameters for the run.

        Returns: True if limits are requested. False if not.
        """
        if "limits" in params:
            if isinstance(params["limits"], bool):
                return params["limits"]
            if params["limits"].lower() in ["on", "yes", "true", "1"]:
                return True
        return False


    @staticmethod
    def checkmetadata(params):
        """Check whether metadata output has been requested.

        Check whether output of metadata has been requested for this output plugin.

        Args:
            params: dict The setup parameters for the run.

        Returns: True if metadata are requested. False if not.
        """
        if "metadata" in params:
            if params["metadata"].lower() in ["on", "yes", "true", "1"]:
                return True
        return False


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
