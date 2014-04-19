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
        try:
            gpsc = GpsController.GpsController()
            # start controller
            gpsc.start()
        # Error
        except Exception as e:
            print "Exception:", e
            raise

    def getVal(self):
        global gpsc
        # we're mobile and outside if speed is above 1.0 m/s
        if gpsc.fix.speed > 1.0:
            return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "mobile", "outdoor")
        else:
            return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "fixed", "indoor")

    def stopController(self):
        global gpsc
        print "Stopping gps controller"
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()
