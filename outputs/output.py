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
    requiredParams = None
    optionalParams = None
    commonParams = None

    @abstractmethod
    def __init__(self, params):
        """Error if sub-class doesn't init itself.

        This is an abstract method, so an error will be raised if a
        sub-class which inherits from this Class doesn't init itself.
        By implication, this means that each output is expected to init
        differently; this is a fair assumption, since a very wide range
        of outputs may be created.

        """
        pass

    @staticmethod
    def checkparams():
        OUTPUTCONFIG = ConfigParser.SafeConfigParser()
        OUTPUTCONFIG.read(CFGPATHS['outputs'])

        OUTPUTNAMES = OUTPUTCONFIG.sections()
        for reqdfield in requiredParams:
            if OUTPUTCONFIG.has_option(name, reqdfield):
                params[reqdfield] = OUTPUTCONFIG.get(name, reqdfield)
            else:
                msg = "Missing required field '" + reqdfield
                msg += "' for plugin " + name + "."
                print(msg)
                msg += "This should be found in file: " + CFGPATHS['outputs']
                msg = format_msg(msg, 'error')
                print(msg)
                raise MissingField
        for optfield in optionalParams:
            if OUTPUTCONFIG.has_option(name, optfield):
                params[optfield] = OUTPUTCONFIG.get(name, optfield)
        for commonfield in common:
            if OUTPUTCONFIG.has_option("Common", commonfield):
                params[commonfield] = OUTPUTCONFIG.get("Common", commonfield)

        # Only applies to output plugins
        if (OUTPUTCONFIG.has_option(name, "metadatareqd") and
            OUTPUTCONFIG.getboolean(name, "metadatareqd")):
            params['metadatareqd'] = True
        else:
            params['metadatareqd'] = False 

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
            return True

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
        "calibration" or "limits") the sub-class may not actually be
        able/designed to ouptput data; in such circumstances the method
        should just return True. In those cases, the method signature
        can have a single 'self' argument as shown above.

        See the docstrings for individual methods within sub-classes for
        more detail on specific cases.

        Args:
            self: self.

        """
        pass

    @abstractmethod
    def output_metadata(self, metadata):
        """Output metadata.

        Output metadata in the format stipulated by this plugin.
        Even if it is not appropriate for the plugin to output metadata
        (e.g. for support plugins), this method is required because
        airpi.py looks for it in when setting up plugins; this is why it
        is abstract.

        In situations where the sub-class defines a support plugin (e.g.
        "calibration" or "limits") the sub-class may not actually be
        able/designed to ouptput metadata; in such circumstances the
        method should just return True. In those cases, the method
        signature remains the same but the value of the 'metadata'
        argument is never used.

        See the docstrings for individual methods within sub-classes for
        more detail on specific cases.

        Args:
            self: self.
            metadata: Dict containing the metadata to be output.

        """
        pass

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

        """
        docal = 0
        if "calibration" in params:
            if params["calibration"].lower() in ["on", "yes", "true", "1"]:
                docal = 1
        return docal

    @staticmethod
    def checklimits(params):
        """Check whether limits have been requested.

        Check whether limits have been requested for this output
        plugin. This will have been done in airpi.py as part of set_up_outputs()
        - more specifically, by define_plugin_params(). This method does not
        actually set any limits; it just records whether or not it
        *should* be done.

        Args:
            params: dict The setup parameters for the run.

        """
        dolimits = 0
        print(params)
        if "limits" in params:
            if params["limits"].lower() in ["on", "yes", "true", "1"]:
                dolimits = 1
        return dolimits

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

class MissingField(Exception):
    """Exception to raise when an imported plugin is missing a required
    field.

    """
    pass
