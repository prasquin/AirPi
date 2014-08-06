import socket
import time
from subprocess import check_output

class Output():
    def __init__(self, params):
        raise NotImplementedError

    def checkCal(self, params):
        doCal = 0;
        if "calibration" in params:
            if params["calibration"].lower() in ["on", "yes", "true", "1"]:
                doCal = 1
        return doCal

    def getserial(self):
        # Extract CPU serial number from cpuinfo
        # From: http://raspberrypi.nxez.com/2014/01/19/getting-your-raspberry-pi-serial-number-using-python.html
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"
        return cpuserial

    def getHostname(self):
        if socket.gethostname().find('.')>=0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]
        return host

    def getMetadata(self):
        #TODO: Somehow grab the operator name
        operator = "Haydy"
        piid = self.getserial()
        metadata  = {"starttime":time.strftime("%H:%M on %A %d %B %Y"), \
        "operator":operator, \
        "piid":piid, \
        "piname":self.getHostname() \
        }
        return metadata
