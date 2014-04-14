#!/usr/bin/env python

import sensor
import GpsController

gpsc = None # define gps data structure

class GPS(sensor.Sensor):
    requiredData = []
    optionalData = []
    def __init__(self, data):
        self.sensorName = "MTK3339"
        self.valName = "Location"
        # start the GPS data polling
        global gpsc
        gpsc = GpsController.GpsController()
        try:
            # start controller
            gpsc.start()
        # Error
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getVal(self):
        global gpsc
        print "Getting gps values", gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, gpsc.fix.speed
        # we're mobile and outside if speed is above 1.0 m/s
        return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "mobile", "outdoor" if gpsc.fix.speed > 1.0 else  "fixed", "indoor")

    def stopController(self):
        global gpsc
        print "Stopping gps controller"
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()
