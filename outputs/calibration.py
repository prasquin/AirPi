"""A module to calibrate sensor data.

A module which is used to support calibration of sensors on an individual basis.
Calibration terms are specified in the AirPi settings config file (usually AirPi/settings.cfg).

"""

import output
import math

class Calibration(output.Output):
    requiredParams = []
    optionalParams = ["Light_Level", "Air_Quality", "Nitrogen_Dioxide", "Carbon_Monoxide", "Volume", "UVI", "Bucket_tips"]
    sharedClass = None

    def __init__(self, params):
        self.calibrations = []
        self.last = []
        self.lastpassed = []
        for i in self.optionalParams:
            if i in params:
                [f, s] = params[i].rsplit(',', 1)
                self.calibrations.append({'name': i, 'function': eval("lambda x: " + f), 'symbol': s})

        if Calibration.sharedClass == None:
            Calibration.sharedClass = self

    def calibrate(self, dataPoints):
        if self.lastpassed == dataPoints:
            # the same dataPoints object, so the calculations would turn out the same
            # so we can just return the result of the last calcs
            return self.last

        self.last = list(dataPoints) # recreate so we don't overwrite un-calibrated data
        for i in range(0, len(self.last)):
            self.last[i] = dict(self.last[i]) # recreate again
            for j in self.calibrations:
                if self.last[i]["name"] == j["name"]:
                    if self.last[i]["value"] != None:
                        self.last[i]["value"] = j["function"](self.last[i]["value"])
                        self.last[i]["symbol"] = j["symbol"]
        self.lastpassed = dataPoints # update which object we last worked on
        return self.last

    def findVal(key):
        print "finding val"
        found = 0
        num = 0
        for i in Calibration.sharedClass.last:
            if i["name"] == key and i["value"] != None:
                found = found + i["value"]
                num += 1
        # average for things like Temperature where we have multiple sensors
        if num != 0:
            found = found / float(num)
        return found
