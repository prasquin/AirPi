from gps import *
from time import sleep
import subprocess
import threading

daemon = None
daemonDelay = 2
class GpsController(threading.Thread):
    def __init__(self, device="/dev/ttyAMA0"):
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

    def startDaemon(self):
        # start the gps daemon
        global daemon
        try:
            daemon = subprocess.Popen(["gpsd","-P","/var/run/gpsd.pid", device])
        except:
            print "Unexpected error, starting daemon:", sys.exc_info()[0]
            raise

    def stopDaemon(self):
        # stop the gps daemon
        global daemon
        daemon.terminate()

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
        gpsc.startDaemon()
        sleep(daemonDelay)
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
        print "Stopping gps controller"
        gpsc.stopController()
        gpsc.stopDaemon()
        # wait for the thread to finish
        gpsc.join()

    print "Done"
