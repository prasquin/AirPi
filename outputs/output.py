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
                docal = 1
        return doCal

    def getMetadata(self):
        #TODO: Somehow grab the operator name
        operator = "Haydy"
        piid = str(check_output('cat /proc/cpuinfo | grep Serial | awk \'{print $3}\'', shell=True))
        if socket.gethostname().find('.')>=0:
            host = socket.gethostname()
        else:
            host = socket.gethostbyaddr(socket.gethostname())[0]
        metadata  = {"starttime":time.strftime("%H:%M on %A %d %B %Y"), \
        "operator":operator, \
        "piid":piid[:piid.rfind('\n')], \
        "piname":host}
        return metadata
