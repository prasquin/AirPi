from gps import *
from time import sleep
import subprocess
import sys
import threading

class GpsSocketError(Exception):
    """Exception to raise when the GPS sock at /var/run/gpsd.sock does
    not exist.

    """
    pass

class GpsController(threading.Thread):

    def __new__(cls):
        """Create new object if socket exists.
        
        Create a new GpsController object. Abort creation of the instance if the
        GPS socket hasn't been set up at /var/run/gpsd.sock.

        """
        if subprocess.call(['test', '-S', '/var/run/gpsd.sock']) != 1:
            return super(GpsController, cls).__new__(cls)
        else:
            print("ERROR:   GPS does not appear to be set up.")
            print("         Try running: \"sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock\"")
            raise GpsSocketError

    def __init__(self):
        """Initialise GpsController class.

        Initialise the GpsController class using parameters passed in
        'data'.

        Args:
            self: self.
            data: A dict containing the parameters to be used during
                  setup.

        """
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE) # starting the stream of info
        self.running = False

    def run(self):
        """Continually get data from gpsd.

        Continually get the data from gpsd, clearing the buffer in the
        process. If we don't do it continually, the buffer will fill up
        and then we're in trouble.

        """
        self.running = True
        while self.running:
            self.gpsd.next()

    def stopController(self):
        """Stop the controller.

        Stop this GPS Controller.

        """
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
    gpsc = GpsController()
    try:
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
    except KeyboardInterrupt:
        print("User cancelled")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()

    print("Done")
