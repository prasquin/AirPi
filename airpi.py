#!/usr/bin/env python

"""This file takes in inputs from a variety of sensor files,
   and outputs information to a variety of services.

"""

#TODO: Warn if no outputs enabeld
#TODO: Put metadata into files or print

import sys
sys.dont_write_bytecode = True

import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os
import signal
import urllib2
import logging, logging.handlers
from math import isnan
from sensors import sensor
from outputs import output
from alerts import alert

cfgdir = "/home/pi/AirPi"
sensorcfg = os.path.join(cfgdir, 'sensors.cfg')
outputscfg = os.path.join(cfgdir, 'outputs.cfg')
settingscfg = os.path.join(cfgdir, 'settings.cfg')
alertscfg = os.path.join(cfgdir, 'alerts.cfg')

LOG_FILENAME = os.path.join(cfgdir, 'airpi.log')
# Set up a specific logger with our desired output level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create handler and add it to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes = 40960, backupCount = 5)
logger.addHandler(handler)
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Uncomment below for more verbose logging output
#logging.basicConfig(level=logging.DEBUG)

def interrupt_handler(signal, frame):
    """Handle the Ctrl+C KeyboardInterrupt by exiting."""
    if gpsPluginInstance:
        gpsPluginInstance.stopController()
    GPIO.output(greenPin, GPIO.LOW)
    GPIO.output(redPin, GPIO.LOW)
    print os.linesep
    print("Stopping sampling as requested...")
    sys.exit(1)

def get_subclasses(mod, cls):
    """Load subclasses for a module.

    Load the named subclasses for a specified module.

    Args:
        mod: Module from which subclass should be loaded.
        cls: Subclass to load

    Returns:
        The subclass.

    """
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj

def check_conn():
    """Check internet connectivity.

    Check whether there is internet connectivity by trying to connect to a website.

    Returns:
        Boolean True if successfully connects to the site within five seconds.
        Boolean False if fails to connect to the site within five seconds.

    """
    try:
        urllib2.urlopen("http://www.google.com", timeout=5)
        return True
    except urllib2.URLError as err:
        pass
    return False

class MissingField(Exception):
    """Exception to be raised when an imported plugin is missing a required field.  """
    pass

if not os.path.isfile(sensorcfg):
    print "Unable to access config file: sensors.cfg"
    logger.error("Unable to access config file: %s" % sensorcfg)
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
                msg = "Error: could not find a subclass of sensor.Sensor in module + filename"
                print(msg)
                logger.error(msg)
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

            for requiredField in reqd:
                if sensorConfig.has_option(i, requiredField):
                    pluginData[requiredField] = sensorConfig.get(i, requiredField)
                else:
                    msg = "Error: Missing required field '" + requiredField
                    msg = msg + "' for sensor plugin " + i
                    print(msg)
                    logger.error(msg)
                    raise MissingField
            for optionalField in opt:
                if sensorConfig.has_option(i, optionalField):
                    pluginData[optionalField] = sensorConfig.get(i, optionalField)
            instClass = sensorClass(pluginData)
            # check for a getVal
            if callable(getattr(instClass, "getVal", None)):
                sensorPlugins.append(instClass)
                # store sensorPlugins array length for GPS plugin
                if i == "GPS":
                    gpsPluginInstance = instClass
                print ("Success: Loaded sensor plugin " + i)
                logger.info("Success: Loaded sensor plugin %s" % i)
            else:
                print ("Success: Loaded support plugin " + i)
                logger.info("Success: Loaded support plugin %s" % i)
    except Exception as e: #add specific exception for missing module
        print("Error: Did not import sensor plugin " + i)
        logger.error("Error: Did not import sensor plugin %s: [%s]" % (i, e))
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
                msg = "Error: could not find a subclass of output.Output in module " + filename
                print(msg)
                logger.error(msg)
                raise

            try:
                reqd = outputClass.requiredParams
            except Exception:
                reqd = []
            try:
                opt = outputClass.optionalParams
            except Exception:
                opt = []
            if outputConfig.has_option(i, "async"):
                async = outputConfig.getboolean(i, "async")
            else:
                async = False

            pluginData = {}
            for requiredField in reqd:
                if outputConfig.has_option(i, requiredField):
                    pluginData[requiredField] = outputConfig.get(i, requiredField)
                else:
                    msg = "Error: Missing required field '" + requiredField
                    msg = msg + "' for output plugin " + i
                    print(msg)
                    logger.error(msg)
                    raise MissingField
            for optionalField in opt:
                if outputConfig.has_option(i, optionalField):
                    pluginData[optionalField] = outputConfig.get(i, optionalField)

            if outputConfig.has_option(i, "needsinternet") and outputConfig.getboolean(i, "needsinternet") and not check_conn():
                msg = "Error: Skipping output plugin " + i + " because no internet connectivity."
                print (msg)
                logger.info(msg)
            else:
                instClass = outputClass(pluginData)
                instClass.async = async

                # check for a outputData function
                if callable(getattr(instClass, "outputData", None)):
                    outputPlugins.append(instClass)
                    print ("Success: Loaded output plugin " + i)
                    logger.info("Success: Loaded output plugin %s" % i)
                else:
                    print ("Success: Loaded support plugin " + i)
                    logger.info("Success: Loaded support plugin %s" % i)

    except Exception as e: #add specific exception for missing module
        print("Error: Did not import output plugin " + i)
        logger.error("Error: Did not import output plugin %s" % i)
        raise e

if not outputPlugins:
    msg = "There are no output plugins enabled! Please enable at least one in outputs.cfg and try again."
    print(msg)
    logger.error(msg)
    sys.exit(1)

if not os.path.isfile(alertscfg):
    print "Unable to access config file: alerts.cfg"
    logger.error("Unable to access config file: %s" % alertscfg)
    exit(1)

alertConfig = ConfigParser.SafeConfigParser()
alertConfig.read(alertscfg)

alertNames = alertConfig.sections()

alertPlugins = []

for i in alertNames:
    try:
        try:
            filename = alertConfig.get(i, "filename")
        except Exception:
            print("Error: no filename config option found for alert plugin " + i)
            logger.error("Error: no filename config option found for alert plugin %s" % i)
            raise
        try:
            enabled = alertConfig.getboolean(i, "enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                mod = __import__('alerts.' + filename, fromlist = ['a']) #Why does this work?
            except Exception:
                print("Error: could not import alert module " + filename)
                logger.error("Error: could not import alert module %s" % filename)
                raise

            try:
                alertClass = get_subclasses(mod, alert.Alert)
                if alertClass == None:
                    raise AttributeError
            except Exception:
                msg = "Error: could not find a subclass of alert.Alert in module " + filename
                print(msg)
                logger.error(msg)
                raise
            try:
                reqd = alertClass.requiredParams
            except Exception:
                reqd = []
            try:
                opt = alertClass.optionalParams
            except Exception:
                opt = []

            if alertConfig.has_option(i, "async"):
                async = alertConfig.getboolean(i, "async")
            else:
                async = False

            pluginData = {}

            for requiredField in reqd:
                if alertConfig.has_option(i, requiredField):
                    pluginData[requiredField] = alertConfig.get(i, requiredField)
                else:
                    msg = "Error: Missing required field '" + requiredField
                    msg = msg + "' for alert plugin " + i
                    print(msg)
                    logger.error(msg)
                    raise MissingField

            for optionalField in opt:
                if alertConfig.has_option(i, optionalField):
                    pluginData[optionalField] = alertConfig.get(i, optionalField)

            if alertConfig.has_option(i, "needsinternet") and alertConfig.getboolean(i, "needsinternet") and not check_conn():
                msg = "Error: Skipping alert plugin " + i + " because no internet connectivity."
                print (msg)
                logger.info(msg)
            else:
                instClass = alertClass(pluginData)
                instClass.async = async

                # check for a sendAlert function
                if callable(getattr(instClass, "sendAlert", None)):
                    alertPlugins.append(instClass)
                    print ("Success: Loaded alert plugin " + i)
                    logger.info("Success: Loaded alert plugin %s" % i)
                else:
                    print ("Error: no callable alert function for alert plugin " + i)
                    logger.info("Error: no callable alert function for alert plugin " + i)

    except Exception as e:
        print("Error: Did not import alert plugin " + i)
        logger.error("Error: Did not import alert plugin " + i)
        raise e



if not os.path.isfile(settingscfg):
    print "Unable to access config file: settings.cfg"
    logger.error("Unable to access config file: %s" % settingscfg)
    exit(1)

mainConfig = ConfigParser.SafeConfigParser()
mainConfig.read(settingscfg)

lastUpdated = 0
delayTime = mainConfig.getfloat("Main", "sampleFreq")
redPin = mainConfig.getint("Main", "redPin")
greenPin = mainConfig.getint("Main", "greenPin")
printErrors = mainConfig.getboolean("Main","printErrors")
successLED = mainConfig.get("Main","successLED")
failLED = mainConfig.get("Main","failLED")
outputSuccessSoFar = False
outputFailSoFar = False

if redPin:
    GPIO.setup(redPin, GPIO.OUT, initial = GPIO.LOW)
if greenPin:
    GPIO.setup(greenPin, GPIO.OUT, initial = GPIO.LOW)

print "Success: Setup complete - starting to sample..."
print "Press Ctrl + C to stop sampling."

# Register the signal handler
signal.signal(signal.SIGINT, interrupt_handler)


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
                    if isnan(val[2]): # this means it has no data to upload.
                        continue
                    logger.debug("GPS output %s" % (val,))
                    # handle GPS data
                    dataDict["latitude"] = val[0]
                    dataDict["longitude"] = val[1]
                    dataDict["altitude"] = val[2]
                    dataDict["disposition"] = val[3]
                    dataDict["exposure"] = val[4]
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                else:
                    dataDict["value"] = i.getVal()
                    dataDict["unit"] = i.valUnit
                    dataDict["symbol"] = i.valSymbol
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                    dataDict["description"] = i.description
                    dataDict["readingType"] = i.readingType
                data.append(dataDict)
            working = True
            try:
                for i in outputPlugins:
                    working = working and i.outputData(data)
                if working:
                    logger.info("Success: Data output in all requested formats.")
                    if greenPin and (successLED == "all" or (successLED == "first" and not outputSuccessSoFar)):
                        GPIO.output(greenPin, GPIO.HIGH)
                    outputSuccessSoFar = True
                else:
                    if not outputFailSoFar:
                        for j in alertPlugins:
                            j.sendAlert()
                    if printErrors:
                        print "Error: Failed to output in all requested formats."
                    logger.info("Failed to output in all requested formats.")
                    if redPin and (failLED in ["all", "constant"] or (failLED == "first" and not outputFailSoFar)):
                        GPIO.output(redPin, GPIO.HIGH)
                    outputFailSoFar = True
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error("Exception: %s" % e)
            else:
                # delay before turning off LED
                time.sleep(1)
                if greenPin:
                    GPIO.output(greenPin, GPIO.LOW)
                if redPin and failLED != "constant":
                    GPIO.output(redPin, GPIO.LOW)
            try:
                time.sleep(delayTime-(time.time()-curTime)-0.01)
            except KeyboardInterrupt:
                raise
            except Exception:
                pass # fall back on old method...
    except KeyboardInterrupt:
        interrupt_handler()
