"""Generic Sensor plugin description (abstract) for sub-classing.

A generic description of a Sensor, which can then be sub-classed for
specific Sensors. This is an abstract base class (ABC) and so cannot be
instantiated directly. A wide and diverse range of sensors is supported,
so there are not too many common properties/functions contained here.

"""
from abc import ABCMeta, abstractmethod

class Sensor(object):
    """Generic Sensor plugin description (abstract) for sub-classing.

    A generic description of a Sensor, which can then be sub-classed for
    specific Sensors. This is an abstract base class (ABC) and so
    cannot be instantiated directly. A wide and diverse range of sensors
    is supported, so there are not too many common properties/functions
    contained here.

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, data):
        """Error if sub-class doesn't init itself.

        This is an abstract method, so an error will be raised if a
        sub-class which inherits from this Class doesn't init itself.
        By implication, this means that each sensor is expected to init
        differently; this is a fair assumption, since a very wide range
        of sensors may be attached.

        """
        pass

    def getname(self):
        """Get Class name (not human-friendly).

        Get the name of the class. Lots of Classes inherit from Sensor,
        so this varies depending on which one we're looking at. Note
        that this isn't necessarily human-friendly, and is often the
        manufacturer's part/reference number for the sensor.

        Returns:
            string The class name.

        """
        return self.__class__.__name__

    def get_sensor_name(self):
        """Get human-friendly Sensor name.

        Get the human-friendly name of the sensor. Lots of Classes
        inherit from Sensor, so this varies depending on which one we're
        looking at.

        Returns:
            string The sensor name.

        """
        return self.valname
