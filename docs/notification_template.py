"""A template AirPi notification plugin.

This file is a basic template which can be used as a base when creating
a custom AirPi notification plugin. You should change the variable names and
function definitions as required, and also add plugin details to the file 
cfg/notifications.cfg"""

# All notification plugins are sub-classes of notification.
import notification

class MyNotificationClass(notification.Notification):
    """A class to send an AirPi notification.

    A class which is used to send a notification relating to an AirPi sensor
    or output error.

    """

    # Parameters listed in requiredParams *MUST* be defined in notifications.cfg
    # Parameters listed in optionalParams can be defined in notifications.cfg if
    # appropriate, but are optional.
    requiredParams = ["firstparamhere", "secondparamhere"]
    optionalParams = ["xthparamhere", "ythparamhere"]
    # Common params are defined in the parent "notification" Class
    commonParams = notification.Notification.commonParams

    def __init__(self, params):
        """
        Initialisation.

        Any initialisation code goes here.
        """
        
        # Use customised messages instead of standard ones, if they are defined.
        if "msgalertsensor" in params:
            self.msgalertsensor = params["msgalertsensor"].replace("<hostname>", hostname)
        else:
            self.msgalertsensor = "AirPi " + hostname + " has experienced a sensor error. It apologies profusely."
        if "msgalertoutput" in params:
            self.msgalertoutput = params["msgalertoutput"].replace("<hostname>", hostname)
        else:
            self.msgalertoutput = "AirPi" + hostname + " has experienced an output error! It apologises profusely."

        if "msgdata" in params:
            self.msgdata = params["msgdata"].replace("<hostname>", hostname)
        else:
            self.msgdata = "Something interesting has happened with AirPi " + hostname + ". You'd better come see this..."

    def sendnotification(self, event):
        """Send a notification.

        Send an AirPi notification.

        Args:
            self: self.
            event: The type of event which the notification should signify.

        """
        try:
            # Send the notification
        except Exception as excep:
            print("Error: " + excep)