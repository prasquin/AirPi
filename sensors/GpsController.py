from gps import *
from time import sleep
import subprocess
import threading

class GpsSocketError(Exception):
    """Exception to raise when the GPS sock at /var/run/gpsd.sock does not
    exist.

    """
    pass

class GpsController(threading.Thread):

    def __new__(cls):
        # Abort creation of the instance if the GPS socket hasn't been set up
        if subprocess.call(['test', '-S', '/var/run/gpsd.sock']) != 1:
            return super(GpsController, cls).__new__(cls)
        else:
            print("ERROR:   GPS does not appear to be set up.")
            print("         Try running: \"sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock\"")
            raise GpsSocketError

    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE) # starting the stream of info
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            # grab EACH set of gpsd info to clear the buffer
            self.gpsd.next()

    def stopController(self):
        self.running = False

    @property
    def fix(self):
        return self.gpsd.fix

    @property
    def utc(self):
        return self.gpsd.utc

    @property
    def satellites(self):
        return self.gpsd.satellites

if __name__ == '__main__':
    # create the controller
    gpsc = GpsController()
    try:
        # start controller
        gpsc.start()
        while True:
            print "latitude ", gpsc.fix.latitude
            print "longitude ", gpsc.fix.longitude
            print "time utc ", gpsc.utc, " + ", gpsc.fix.time
            print "altitude (m)", gpsc.fix.altitude
            print "eps ", gpsc.fix.eps
            print "epx ", gpsc.fix.epx
            print "epv ", gpsc.fix.epv
            print "ept ", gpsc.fix.ept
            print "speed (m/s) ", gpsc.fix.speed
            print "climb ", gpsc.fix.climb
            print "track ", gpsc.fix.track
            print "mode ", gpsc.fix.mode
            print "sats ", gpsc.satellites
            sleep(0.5)

    # Ctrl C
    except KeyboardInterrupt:
        print "User cancelled"

    # Error
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    finally:
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()

    print "Done"
