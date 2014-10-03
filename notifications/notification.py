import socket

class Notification():
    commonParams = ["msgalertsensor", "msgalertoutput", "msgdata"]

    def __init__(self, params):
        raise NotImplementedError

    def getHostname(self):
        """Get current hostname.

        Get the current hostname of the Raspberry Pi.

        Returns:
            string The hostname.

        """
        if socket.gethostname().find('.')>=0:
            return socket.gethostname()
        else:
            return socket.gethostbyaddr(socket.gethostname())[0]
