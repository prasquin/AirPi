#!/usr/bin/python3

""" Read low-level data from DS18B20 sensor.

A low-level Class to read data directly from the DS18B20 sensor,
which provides temperature.

You must add these lines in /etc/modules
w1-gpio
w1-therm

You must add this line to the bottom of /boot/config.txt
dtoverlay=w1-gpio

"""

import os, glob, time

class DS18B20(object):
    def __init__(self, id='28-00047620aabb', debug=False):
        self.debug = debug
        self.device_file = glob.glob('/sys/bus/w1/devices/' + str(id))[0] + '/w1_slave'
    
    def readrawtemp(self):
        f = open(self.device_file, 'r')
        line = f.readlines()
        f.close()
        return line
        
    def crccheck(self, lines):
        return lines[0].strip()[-3:] == "YES"

    def readTemperature(self):
        i = 0
        lines = self.readrawtemp()
        success = self.crccheck(lines)
        while not success and i < 2:
            time.sleep(0.2)
            lines = self.readrawtemp()
            success = self.crccheck(lines)
            i += 1
        if success:
            pos = lines[1].find('t=')
            if pos != -1:
                val = lines[1][pos+2:]
                return float(val)/1000.0
            else:
                print("Error: Data temperature sensor DS18B20 error")
                return False
        else:
	    print("Error: Temperature sensor DS18B20 not found")
            return False

if __name__ == "__main__":
    obj = DS18B20()
    print("Temp: %s C" % obj.readTemperature())
