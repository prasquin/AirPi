import socket

class Notification():
    commonParams = ["msgalertsensor", "msgalertoutput", "msgdata"]

    def __init__(self, params):
        raise NotImplementedError

    def getHostname(self):
        if socket.gethostname().find('.')>=0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]
        return host
