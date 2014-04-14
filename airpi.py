#!/usr/bin/env python

#This file takes in inputs from a variety of sensor files, and outputs information to a variety of services
import sys
sys.dont_write_bytecode = True

import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os
from sys import exit
from sensors import sensor
from outputs import output

# add logging support
import logging, logging.handlers
LOG_FILENAME = os.path.join("/var/log/airpi" , 'airpi.log')
# Set up a specific logger with our desired output level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create handler and add it to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes = 40960, backupCount = 5)
logger.addHandler(handler)
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

cfgdir = "/usr/local/etc/airpi"
sensorcfg = os.path.join(cfgdir, 'sensors.cfg')
outputscfg = os.path.join(cfgdir, 'outputs.cfg')
settingscfg = os.path.join(cfgdir, 'settings.cfg')

def get_subclasses(mod,cls):
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj


if not os.path.isfile(sensorcfg):
    print "Unable to access config file: sensors.cfg"
    logger.error("Unable to access config file: %s" % sensorscfg)
    exit(1)

sensorConfig = ConfigParser.SafeConfigParser()
sensorConfig.read(sensorcfg)

sensorNames = sensorConfig.sections()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #Use BCM GPIO numbers.

sensorPlugins = []
gpsPluginInstance = None
for i in sensorNames:
    try:
        try:
            filename = sensorConfig.get(i,"filename")
        except Exception:
            print("Error: no filename config option found for sensor plugin " + i)
            logger.error("Error: no filename config option found for sensor plugin %s" % i)
            raise
        try:
            enabled = sensorConfig.getboolean(i,"enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                mod = __import__('sensors.' + filename, fromlist = ['a']) #Why does this work?
            except Exception:
                print("Error: could not import sensor module " + filename)
                logger.error("Error: could not import sensor module %s" % filename)
                raise

            try:
                sensorClass = get_subclasses(mod, sensor.Sensor)
                if sensorClass == None:
                    raise AttributeError
            except Exception:
                print("Error: could not find a subclass of sensor.Sensor in module " + filename)
                logger.error("Error: could not find a subclass of sensor.Sensor in module %s" % filename)
                raise

            try:
                reqd = sensorClass.requiredData
            except Exception:
                reqd = []
            try:
                opt = sensorClass.optionalData
            except Exception:
                opt = []

            pluginData = {}

            class MissingField(Exception): pass

            for requiredField in reqd:
                if sensorConfig.has_option(i, requiredField):
                    pluginData[requiredField] = sensorConfig.get(i, requiredField)
                else:
                    print "Error: Missing required field '" + requiredField + "' for sensor plugin " + i
                    logger.error("Error: Missing required field %s for sensor plugin %s" % (requiredField, i))
                    raise MissingField
            for optionalField in opt:
                if sensorConfig.has_option(i, optionalField):
                    pluginData[optionalField] = sensorConfig.get(i, optionalField)
            instClass = sensorClass(pluginData)
            sensorPlugins.append(instClass)
            # store sensorPlugins array length for GPS plugin
            if i == "GPS":
                gpsPluginInstance = instClass
            print ("Success: Loaded sensor plugin " + i)
            logger.info("Success: Loaded sensor plugin %s" % i)
    except Exception as e: #add specific exception for missing module
        print("Error: Did not import sensor plugin " + i )
        logger.error("Error: Did not import sensor plugin %s" % i)
        raise e


if not os.path.isfile(outputscfg):
    print "Unable to access config file: outputs.cfg"
    logger.error("Unable to access config file: %s" % outputscfg)
    exit(1)

outputConfig = ConfigParser.SafeConfigParser()
outputConfig.read(outputscfg)

outputNames = outputConfig.sections()

outputPlugins = []

for i in outputNames:
    try:
        try:
            filename = outputConfig.get(i, "filename")
        except Exception:
            print("Error: no filename config option found for output plugin " + i)
            logger.error("Error: no filename config option found for output plugin %s" % i)
            raise
        try:
            enabled = outputConfig.getboolean(i, "enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                mod = __import__('outputs.' + filename, fromlist = ['a']) #Why does this work?
            except Exception:
                print("Error: could not import output module " + filename)
                logger.error("Error: could not import output module %s" % filename)
                raise

            try:
                outputClass = get_subclasses(mod, output.Output)
                if outputClass == None:
                    raise AttributeError
            except Exception:
                print("Error: could not find a subclass of output.Output in module " + filename)
                logger.error("Error: could not find a subclass of output.Output in module %s" % filename)
                raise
            try:
                reqd = outputClass.requiredData
            except Exception:
                reqd = []
            try:
                opt = outputClass.optionalData
            except Exception:
                opt = []

            if outputConfig.has_option(i, "async"):
                async = outputConfig.getbool(i, "async")
            else:
                async = False

            pluginData = {}

            class MissingField(Exception): pass

            for requiredField in reqd:
                if outputConfig.has_option(i, requiredField):
                    pluginData[requiredField] = outputConfig.get(i, requiredField)
                else:
                    print "Error: Missing required field '" + requiredField + "' for output plugin " + i
                    logger.error("Error: Missing required field %s for output plugin %s" % (requiredField, i))
                    raise MissingField
            for optionalField in opt:
                if outputConfig.has_option(i, optionalField):
                    pluginData[optionalField] = outputConfig.get(i, optionalField)
            instClass = outputClass(pluginData)
            instClass.async = async
            outputPlugins.append(instClass)
            print ("Success: Loaded output plugin " + i)
            logger.info("Success: Loaded output plugin %s" % i)
    except Exception as e: #add specific exception for missing module
        print("Error: Did not import output plugin " + i)
        logger.error("Error: Did not import output plugin %s" % i)
        raise e

if not os.path.isfile(settingscfg):
    print "Unable to access config file: settings.cfg"
    logger.error("Unable to access config file: %s" % settingscfg)
    exit(1)

mainConfig = ConfigParser.SafeConfigParser()
mainConfig.read(settingscfg)

lastUpdated = 0
delayTime = mainConfig.getfloat("Main", "uploadDelay")
redPin = mainConfig.getint("Main", "redPin")
greenPin = mainConfig.getint("Main", "greenPin")
GPIO.setup(redPin, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(greenPin, GPIO.OUT, initial = GPIO.LOW)
while True:
    try:
        curTime = time.time()
        if (curTime - lastUpdated) > delayTime:
            lastUpdated = curTime
            data = []
            #Collect the data from each sensor
            for i in sensorPlugins:
                dataDict = {}
                if i == gpsPluginInstance:
                    val = i.getVal()
                    logger.debug("GPS output", val)
                    if val[1] == None: #this means it has no data to upload.
                        continue
                    # handle GPS data
                    dataDict["name"] = "Location"
                    dataDict["Latitude"] = val[1]
                    dataDict["Longitude"] = val[2]
                    dataDict["Altitude"] = val[3]
                    dataDict["Disposition"] = val[4]
                    dataDict["Exposure"] = val[5]
                else:
                    val = i.getVal()
                    if val == None: #this means it has no data to upload.
                        continue
                    dataDict["value"] = val
                    dataDict["unit"] = i.valUnit
                    dataDict["symbol"] = i.valSymbol
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                data.append(dataDict)
            working = True
            try:
                for i in outputPlugins:
                    working = working and i.outputData(data)
                if working:
                    print "Uploaded successfully"
                    logger.info("Uploaded successfully")
                    GPIO.output(greenPin, GPIO.HIGH)
                else:
                    print "Failed to upload"
                    logger.info("Failed to upload")
                    GPIO.output(redPin, GPIO.HIGH)
            except Exception as e:
                logger.error("Exception: %s, %d" % (e, time.time()))
                # # set correct time if SSL certificate verify error
                # if "certificate verify failed" in e and time.time() < 5000:
                #     os.system("getTime.sh")
            else:
                time.sleep(1)
                GPIO.output(greenPin, GPIO.LOW)
                GPIO.output(redPin, GPIO.LOW)
    except KeyboardInterrupt:
        print "KeyboardInterrupt detected"
        if gpsPluginInstance:
            gpsPluginInstance.stopController()
        sys.exit(1)
