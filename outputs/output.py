import time
import socket
from subprocess import check_output

class Output(object):
    def __init__(self, params):
        raise NotImplementedError

    def checkCal(self, params):
        doCal = 0;
        if "calibration" in params:
            if params["calibration"].lower() in ["on", "yes", "true", "1"]:
                doCal = 1
        return doCal

    def getHostname(self):
        if socket.gethostname().find('.')>=0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]
        return host
