#!/usr/bin/env python

"""This file takes in inputs from a variety of sensor files,
   and outputs information to a variety of services.

"""

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
from datetime import datetime
from math import isnan
from sensors import sensor
from outputs import output
from notifications import notification

CFGDIR = "/home/pi/AirPi2.7"
SENSORSCFG = os.path.join(CFGDIR, 'sensors.cfg')
OUTPUTSCFG = os.path.join(CFGDIR, 'outputs.cfg')
SETTINGSCFG = os.path.join(CFGDIR, 'settings.cfg')
NOTIFICATIONSCFG = os.path.join(CFGDIR, 'notifications.cfg')

LOG_FILENAME = os.path.join(CFGDIR, 'airpi.log')
# Set up a specific logger with our desired output level
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# create handler and add it to the logger
HANDLER = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=40960, backupCount=5)
LOGGER.addHandler(HANDLER)
# create formatter and add it to the handler
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
# Uncomment below for more verbose logging output
#logging.basicConfig(level=logging.DEBUG)

def interrupt_handler(signal, frame):
    """Handle the Ctrl+C KeyboardInterrupt by exiting."""
    if gpsPluginInstance:
        gpsPluginInstance.stopController()
    GPIO.output(GREENPIN, GPIO.LOW)
    GPIO.output(REDPIN, GPIO.LOW)
    print(os.linesep)
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

    Check for internet connectivity by trying to connect to a website.

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
    """Exception to be raised when an imported plugin is missing a required field.

    """
    pass

if not os.path.isfile(SENSORSCFG):
    msg = "Unable to access config file: " + SENSORSCFG
    print(msg)
    LOGGER.error(msg)
    exit(1)

SENSORCONFIG = ConfigParser.SafeConfigParser()
SENSORCONFIG.read(SENSORSCFG)

SENSORNAMES = SENSORCONFIG.sections()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #Use BCM GPIO numbers.

sensorPlugins = []
gpsPluginInstance = None

for i in SENSORNAMES:
    try:
        try:
            filename = SENSORCONFIG.get(i, "filename")
        except Exception:
            msg = "Error: no filename config option found for sensor plugin " + str(i)
            print(msg)
            LOGGER.error(msg)
            raise
        try:
            enabled = SENSORCONFIG.getboolean(i, "enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                # 'a' means nothing below, but argument must be non-null
                mod = __import__('sensors.' + filename, fromlist = ['a'])
            except Exception:
                msg = "Error: could not import sensor module " + filename
                print(msg)
                LOGGER.error(msg)
                raise

            try:
                sensorClass = get_subclasses(mod, sensor.Sensor)
                if sensorClass == None:
                    raise AttributeError
            except Exception:
                msg = "Error: could not find a subclass of sensor.Sensor"
                msg += " in module " + filename
                print(msg)
                LOGGER.error(msg)
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

            for reqdField in reqd:
                if SENSORCONFIG.has_option(i, reqdField):
                    pluginData[reqdField] = SENSORCONFIG.get(i, reqdField)
                else:
                    msg = "Error: Missing required field '" + reqdField
                    msg += "' for sensor plugin " + i + "." + os.linesep
                    msg += "Error: This should be found in file: " + SENSORSCFG
                    print(msg)
                    LOGGER.error(msg)
                    raise MissingField
            for optField in opt:
                if SENSORCONFIG.has_option(i, optField):
                    pluginData[optField] = SENSORCONFIG.get(i, optField)
            instClass = sensorClass(pluginData)
            # check for a getVal
            if callable(getattr(instClass, "getVal", None)):
                sensorPlugins.append(instClass)
                # store sensorPlugins array length for GPS plugin
                if i == "GPS":
                    gpsPluginInstance = instClass
                msg = "Success: Loaded sensor plugin " + str(i)
                print(msg)
                LOGGER.info(msg)
            else:
                msg = "Success: Loaded support plugin " + str(i)
                print(msg)
                LOGGER.info(msg)
    except Exception as excep: # TODO: add specific exception for missing module
        msg = "Error: Did not import sensor plugin " + str(i) + ": " + str(excep)
        print(msg)
        LOGGER.error(msg)
        raise excep



if not os.path.isfile(OUTPUTSCFG):
    msg = "Unable to access config file: " + OUTPUTSCFG
    print(msg)
    LOGGER.error(msg)
    exit(1)

OUTPUTCONFIG = ConfigParser.SafeConfigParser()
OUTPUTCONFIG.read(OUTPUTSCFG)

OUTPUTNAMES = OUTPUTCONFIG.sections()

outputPlugins = []

metadata = None

for i in OUTPUTNAMES:
    try:
        try:
            filename = OUTPUTCONFIG.get(i, "filename")
        except Exception:
            msg = "Error: no filename config option found for output plugin " + str(i)
            print(msg)
            LOGGER.error(msg)
            raise
        try:
            enabled = OUTPUTCONFIG.getboolean(i, "enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                # 'a' means nothing below, but argument must be non-null
                mod = __import__('outputs.' + filename, fromlist = ['a'])
            except Exception:
                msg = "Error: could not import output module " + filename
                print(msg)
                LOGGER.error(msg)
                raise

            try:
                outputClass = get_subclasses(mod, output.Output)
                if outputClass == None:
                    raise AttributeError
            except Exception:
                msg = "Error: could not find a subclass of output.Output in module " + filename
                print(msg)
                LOGGER.error(msg)
                raise

            try:
                reqd = outputClass.requiredParams
            except Exception:
                reqd = []
            try:
                opt = outputClass.optionalParams
            except Exception:
                opt = []
            if OUTPUTCONFIG.has_option(i, "async"):
                async = OUTPUTCONFIG.getboolean(i, "async")
            else:
                async = False

            pluginData = {}
            for reqdField in reqd:
                if OUTPUTCONFIG.has_option(i, reqdField):
                    pluginData[reqdField] = OUTPUTCONFIG.get(i, reqdField)
                else:
                    msg = "Error: Missing required field '" + reqdField
                    msg += "' for output plugin " + i + "." + os.linesep
                    msg += "Error: This should be found in file: " + OUTPUTSCFG
                    print(msg)
                    LOGGER.error(msg)
                    raise MissingField
            for optField in opt:
                if OUTPUTCONFIG.has_option(i, optField):
                    pluginData[optField] = OUTPUTCONFIG.get(i, optField)

            if OUTPUTCONFIG.has_option(i, "needsinternet"):
                if OUTPUTCONFIG.getboolean(i, "needsinternet") and not check_conn():
                    msg = "Error: Skipping output plugin " + i + " because no internet connectivity."
                    print (msg)
                    LOGGER.info(msg)
            else:
                instClass = outputClass(pluginData)
                instClass.async = async

                # check for a outputData function
                if callable(getattr(instClass, "outputData", None)):
                    outputPlugins.append(instClass)
                    msg = "Success: Loaded output plugin " + str(i)
                    print(msg)
                    LOGGER.info(msg)
                else:
                    msg = "Success: Loaded support plugin " + str(i)
                    print(msg) 
                    LOGGER.info(msg)

                # Check for an outputMetadata function
                if OUTPUTCONFIG.has_option(i, "metadatareqd") and OUTPUTCONFIG.getboolean(i, "metadatareqd"):
                    if callable(getattr(instClass, "outputMetadata", None)):
                        # We'll print this later on
                        metadata = instClass.outputMetadata();

    except Exception as excep: #add specific exception for missing module
        msg = "Error: Did not import output plugin " + str(i) + ": " + str(excep)
        print(msg)
        LOGGER.error(msg)
        raise excep

if not outputPlugins:
    msg = "There are no output plugins enabled! Please enable at least one in 'outputs.cfg' and try again."
    print(msg)
    LOGGER.error(msg)
    sys.exit(1)

if not os.path.isfile(NOTIFICATIONSCFG):
    msg = "Unable to access config file: " + NOTIFICATIONSCFG
    print(msg)
    LOGGER.error(msg)
    exit(1)

NOTIFICATIONCONFIG = ConfigParser.SafeConfigParser()
NOTIFICATIONCONFIG.read(NOTIFICATIONSCFG)

NOTIFICATIONNAMES = NOTIFICATIONCONFIG.sections()
NOTIFICATIONNAMES.remove("Common")

notificationPlugins = []

for i in NOTIFICATIONNAMES:
    try:
        try:
            filename = NOTIFICATIONCONFIG.get(i, "filename")
        except Exception:
            msg = "Error: no filename config option found for notification plugin " + str(i)
            print(msg)
            LOGGER.error(msg)
            raise
        try:
            enabled = NOTIFICATIONCONFIG.getboolean(i, "enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                # 'a' means nothing below, but argument must be non-null
                mod = __import__('notifications.' + filename, fromlist = ['a'])
            except Exception:
                msg = "Error: could not import notification module " + filename
                print(msg)
                LOGGER.error(msg)
                raise

            try:
                notificationClass = get_subclasses(mod, notification.Notification)
                if notificationClass == None:
                    raise AttributeError
            except Exception:
                msg = "Error: could not find a subclass of notification.Notification in module " + filename
                print(msg)
                LOGGER.error(msg)
                raise
            try:
                reqd = notificationClass.requiredParams
            except Exception:
                reqd = []
            try:
                opt = notificationClass.optionalParams
            except Exception:
                opt = []
            try:
                common = notificationClass.commonParams
            except Exception:
                common = []

            if NOTIFICATIONCONFIG.has_option(i, "async"):
                async = NOTIFICATIONCONFIG.getboolean(i, "async")
            else:
                async = False

            pluginData = {}

            for reqdField in reqd:
                if NOTIFICATIONCONFIG.has_option(i, reqdField):
                    pluginData[reqdField] = NOTIFICATIONCONFIG.get(i, reqdField)
                else:
                    msg = "Error: Missing required field '" + reqdField
                    msg += "' for notification plugin " + i + "." + os.linesep
                    msg += "Error: This should be found in file: " + NOTIFICATIONSCFG
                    print(msg)
                    LOGGER.error(msg)
                    raise MissingField

            for optField in opt:
                if NOTIFICATIONCONFIG.has_option(i, optField):
                    pluginData[optField] = NOTIFICATIONCONFIG.get(i, optField)

            for commonField in common:
                if NOTIFICATIONCONFIG.has_option("Common", commonField):
                    pluginData[commonField] = NOTIFICATIONCONFIG.get("Common", commonField)
            
            if NOTIFICATIONCONFIG.has_option(i, "needsinternet"):
                if NOTIFICATIONCONFIG.getboolean(i, "needsinternet") and not check_conn():
                    msg = "Error: Skipping notification plugin " + i + " because no internet connectivity."
                    print (msg)
                    LOGGER.info(msg)
                else:
                    instClass = notificationClass(pluginData)
                    instClass.async = async

                # check for a sendNotification function
                if callable(getattr(instClass, "sendNotification", None)):
                    notificationPlugins.append(instClass)
                    msg = "Success: Loaded notification plugin " + str(i)
                    print(msg)
                    LOGGER.info(msg)
                else:
                    msg = "Error: no callable sendNotification() function for notification plugin " + str(i)
                    print(msg)
                    LOGGER.info(msg)

    except Exception as excep:
        msg = "Error: Did not import notification plugin " + str(i) + ": " + str(excep)
        print(msg)
        LOGGER.error(msg)
        raise excep

if not os.path.isfile(SETTINGSCFG):
    msg = "Unable to access config file: " + SETTINGSCFG
    print(msg)
    LOGGER.error(msg)
    exit(1)

MAINCONFIG = ConfigParser.SafeConfigParser()
MAINCONFIG.read(SETTINGSCFG)

lastUpdated = 0
SAMPLEFREQ = MAINCONFIG.getfloat("Main", "sampleFreq")
OPERATOR = MAINCONFIG.get("Main", "operator")
REDPIN = MAINCONFIG.getint("Main", "redPin")
GREENPIN = MAINCONFIG.getint("Main", "greenPin")
PRINTERRORS = MAINCONFIG.getboolean("Main","printErrors")
SUCCESSLED = MAINCONFIG.get("Main","successLED")
FAILLED = MAINCONFIG.get("Main","failLED")
greenHasLit = False
redHasLit = False

if REDPIN:
    GPIO.setup(REDPIN, GPIO.OUT, initial=GPIO.LOW)
if GREENPIN:
    GPIO.setup(GREENPIN, GPIO.OUT, initial=GPIO.LOW)

# Register the signal handler
signal.signal(signal.SIGINT, interrupt_handler)

print("Success: Setup complete.")
if metadata is not None:
    print("==========================================================")
    print(metadata)
    print("==========================================================")
    del metadata

RIGHTNOW = datetime.now()
SECONDS = float(RIGHTNOW.second + (RIGHTNOW.microsecond / 1000000))
DELAY = (60 - SECONDS)
del RIGHTNOW
del SECONDS
print("Sampling will start in " + str(int(DELAY)) + " seconds...")
print("Press Ctrl + C to stop sampling.")
print("==========================================================")
time.sleep(DELAY)
del DELAY

while True:
    try:
        curTime = time.time()
        sampleTime = None
        if (curTime - lastUpdated) > SAMPLEFREQ:
            lastUpdated = curTime
            data = []
            alreadySentSensorAlerts = False
            alreadySentOutputAlerts = False
            #Collect the data from each sensor
            sensorsWorking = True
            for i in sensorPlugins:
                dataDict = {}
                if i == gpsPluginInstance:
                    sampleTime = datetime.now()
                    val = i.getVal()
                    if isnan(val[2]): # this means it has no data to upload.
                        continue
                    LOGGER.debug("GPS output %s" % (val,))
                    # handle GPS data
                    dataDict["latitude"] = val[0]
                    dataDict["longitude"] = val[1]
                    dataDict["altitude"] = val[2]
                    dataDict["disposition"] = val[3]
                    dataDict["exposure"] = val[4]
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                else:
                    sampletime = datetime.now()
                    dataDict["value"] = i.getVal()
                    # TODO: Ensure this is robust
                    if dataDict["value"] is None or isnan(float(dataDict["value"])) or dataDict["value"] == 0:
                        sensorsWorking = False
                    dataDict["unit"] = i.valUnit
                    dataDict["symbol"] = i.valSymbol
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                    dataDict["description"] = i.description
                    dataDict["readingType"] = i.readingType
                data.append(dataDict)
            # Record the outcome
            if sensorsWorking:
                LOGGER.info("Success: Data obtained from all sensors.")
            else:
                if not alreadySentSensorAlerts:
                    for j in notificationPlugins:
                        j.sendNotification("alertsensor")
                    alreadySentSensorAlerts = True
                msg = "Error: Failed to obtain data from all sensors."
                LOGGER.error(msg)
                if PRINTERRORS:
                    print(msg)
            # Output data
            try:
                outputsWorking = True
                for i in outputPlugins:
                    outputsWorking = i.outputData(data)
                # Record the outcome
                if outputsWorking:
                    LOGGER.info("Success: Data output in all requested formats.")
                    if GREENPIN and (SUCCESSLED == "all" or (SUCCESSLED == "first" and not greenHasLit)):
                        GPIO.output(GREENPIN, GPIO.HIGH)
                        greenHasLit = True
                else:
                    if not alreadySentOutputAlerts:
                        for j in notificationPlugins:
                            j.sendNotification("alertoutput")
                        alreadySentOutputAlerts = True
                    msg = "Error: Failed to output in all requested formats."
                    LOGGER.error(msg)
                    if PRINTERRORS:
                        print(msg)
                    if REDPIN and (FAILLED in ["all", "constant"] or (FAILLED == "first" and not redHasLit)):
                        GPIO.output(REDPIN, GPIO.HIGH)
                        redHasLit = True
            except KeyboardInterrupt:
                raise
            except Exception as excep:
                LOGGER.error("Exception: %s" % excep)
            else:
                # Delay before turning off LED
                time.sleep(1)
                if GREENPIN:
                    GPIO.output(GREENPIN, GPIO.LOW)
                if REDPIN and FAILLED != "constant":
                    GPIO.output(REDPIN, GPIO.LOW)
        try:
            time.sleep(SAMPLEFREQ -(time.time()-curTime)-0.01)
        except KeyboardInterrupt:
            raise
        except Exception:
            pass # fall back on old method...
    except KeyboardInterrupt:
        interrupt_handler()
