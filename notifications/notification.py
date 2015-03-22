"""Generic Notification plugin description (abstract) for sub-classing.

A generic description of an Notification plugin, which can then be
sub-classed for specific Notifications. This is an abstract base class
(ABC) and so cannot be instantiated directly.

"""
from abc import ABCMeta, abstractmethod
import socket

class Notification():
    """Generic Notification plugin description (abstract) for
    sub-classing.

    A generic description of an Notification plugin, which can then be
    sub-classed for specific Notification. This is an abstract base
    class (ABC) and so cannot be instantiated directly.

    """
    commonParams = ["msgalertsensor", "msgalertoutput", "msgdata"]

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, params):
        """Error if sub-class doesn't init itself.

        This is an abstract method, so an error will be raised if a
        sub-class which inherits from this Class doesn't init itself.
        By implication, this means that each notification is expected to
        init differently; this is a fair assumption, since a very wide
        range of notifications may be created.

        """
        pass

    @abstractmethod
    def sendnotification(self, dummy):
        """Send a notification.

        Send a notification when an appropriate event is detected. The
        format of the notification will depend on the exact plugin.
        All notification plugins must implement actually sending a
        notification, hence this method is abstract.

        The second argument here is named 'dummy' to facilitate
        compliance with Pylint. In reality it would be called 'event'.

        Args:
            self: self.
            dummy: string The type of event the notification represents.

        """
        pass

    def gethostname(self):
        """Get current hostname.

        Get the current hostname of the Raspberry Pi.

        Returns:
            string The hostname.

        """
        if socket.gethostname().find('.') >= 0:
            return socket.gethostname()
        else:
            return socket.gethostbyaddr(socket.gethostname())[0]
