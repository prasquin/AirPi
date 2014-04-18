from gps import *
import time
import subprocess
import threading

daemon = None
class GpsController(threading.Thread):
    def __init__(self):
        global daemon
        # start the gps daemon first
        try:
            subprocess.Popen(["chown",":dialout", "/dev/ttyAMA0"]) # make UART device accessible to gpsd
            daemon = subprocess.Popen(["gpsd","-P","/var/run/gpsd.pid", "/dev/ttyAMA0"])
        except
            print "Unexpected error, starting the daemon:", sys.exc_info()[0]
            raise

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
        # stop the gps daemon
        global daemon
        self.daemon.terminate()

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
            time.sleep(0.5)

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
        # wait for the thread to finish
        gpsc.join()

    print "Done"
