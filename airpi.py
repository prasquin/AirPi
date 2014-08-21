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

class MissingField(Exception):
    """Exception to be raised when an imported plugin is missing a required field.

    """
    pass

def interrupt_handler(signal, frame):
    """Handle the Ctrl+C KeyboardInterrupt by exiting."""
    if gpsPluginInstance:
        gpsPluginInstance.stopController()
    led_off(settings['GREENPIN'])
    led_off(settings['REDPIN'])
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

def check_plugins_enabled(plugins, type):
    if not plugins:
        msg = "There are no " + type + " plugins enabled! Please enable at least one and try again."
        print(msg)
        LOGGER.error(msg)
        sys.exit(1)
    else:
        return True

def led_setup(redpin, greenpin):
    if redpin:
        GPIO.setup(redpin, GPIO.OUT, initial=GPIO.LOW)
    if redpin:
        GPIO.setup(greenpin, GPIO.OUT, initial=GPIO.LOW)

def led_on(pin):
    GPIO.output(pin, GPIO.HIGH)

def led_off(pin):
    GPIO.output(pin, GPIO.LOW)

def set_paths():
    cfgpaths = {}
    basedir = os.getcwd()
    cfgdir = os.path.join(basedir, 'cfg')
    cfgpaths['settings'] = os.path.join(cfgdir, 'settings.cfg')
    cfgpaths['sensors'] = os.path.join(cfgdir, 'sensors.cfg')
    cfgpaths['outputs'] = os.path.join(cfgdir, 'outputs.cfg')
    cfgpaths['notifications'] = os.path.join(cfgdir, 'notifications.cfg')
    logdir = os.path.join(basedir, 'log')
    cfgpaths['log'] = os.path.join(logdir, 'airpi.log')
    return cfgpaths

def check_cfg_file(filetocheck):
    if not os.path.isfile(filetocheck):
        msg = "Unable to access config file: " + filetocheck
        print(msg)
        LOGGER.error(msg)
        exit(1)
    else:
        msg = "Config file: " + filetocheck
        LOGGER.info(msg)

def set_up_sensors():
    
    print("==========================================================")
    print("Loading SENSORS...")

    check_cfg_file(CFGPATHS['sensors'])

    SENSORCONFIG = ConfigParser.SafeConfigParser()
    SENSORCONFIG.read(CFGPATHS['sensors'])

    SENSORNAMES = SENSORCONFIG.sections()

    sensorPlugins = []

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM) #Use BCM GPIO numbers.

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
                        msg += "Error: This should be found in file: " + CFGPATHS['sensors']
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

    if check_plugins_enabled(sensorPlugins, 'sensor'):
        return sensorPlugins

def set_up_outputs():
    
    print("==========================================================")
    print("Loading OUTPUTS...")

    check_cfg_file(CFGPATHS['outputs'])

    OUTPUTCONFIG = ConfigParser.SafeConfigParser()
    OUTPUTCONFIG.read(CFGPATHS['outputs'])

    OUTPUTNAMES = OUTPUTCONFIG.sections()

    outputPlugins = []

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
                        msg += "Error: This should be found in file: " + CFGPATHS['outputs']
                        print(msg)
                        LOGGER.error(msg)
                        raise MissingField
                for optField in opt:
                    if OUTPUTCONFIG.has_option(i, optField):
                        pluginData[optField] = OUTPUTCONFIG.get(i, optField)

                if OUTPUTCONFIG.has_option(i, "needsinternet") and OUTPUTCONFIG.getboolean(i, "needsinternet") and not check_conn():
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
                            # For CSVOutput it writes to file immediately.
                            # For printing, we have to save it and use it later
                            if filename != "print":
                                instClass.outputMetadata()
                            else:
                                metadata = instClass.outputMetadata()

        except Exception as excep: #add specific exception for missing module
            msg = "Error: Did not import output plugin " + str(i) + ": " + str(excep)
            print(msg)
            LOGGER.error(msg)
            raise excep

    if check_plugins_enabled(outputPlugins, 'output'):
        return outputPlugins

def set_up_notifications():

    print("==========================================================")
    print("Loading NOTIFICATIONS...")

    check_cfg_file(CFGPATHS['notifications'])

    NOTIFICATIONCONFIG = ConfigParser.SafeConfigParser()
    NOTIFICATIONCONFIG.read(CFGPATHS['notifications'])

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
                        msg += "Error: This should be found in file: " + CFGPATHS['notifications']
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

    # Don't run check_plugins_enabled here, because it's OK to not have any notifications
    if not notificationPlugins:
        print("Info: No Notifications requested.")
    return notificationPlugins

def set_settings():

    print("==========================================================")
    print("Loading SETTINGS...")

    check_cfg_file(CFGPATHS['settings'])
    mainconfig = ConfigParser.SafeConfigParser()
    mainconfig.read(CFGPATHS['settings'])
    settingsList = {}

    settingsList['SAMPLEFREQ'] = mainconfig.getfloat("Main", "sampleFreq")
    settingsList['OPERATOR'] = mainconfig.get("Main", "operator")
    settingsList['REDPIN'] = mainconfig.getint("Main", "redPin")
    settingsList['GREENPIN'] = mainconfig.getint("Main", "greenPin")
    settingsList['PRINTERRORS'] = mainconfig.getboolean("Main","printErrors")
    settingsList['SUCCESSLED'] = mainconfig.get("Main","successLED")
    settingsList['FAILLED'] = mainconfig.get("Main","failLED")
    return settingsList

def delay_start(timenow):
    SECONDS = float(timenow.second + (timenow.microsecond / 1000000))
    DELAY = (60 - SECONDS)
    if DELAY != 60:
        print("Info: Sampling will start in " + str(int(DELAY)) + " seconds...")
        print("==========================================================")
        time.sleep(DELAY)

def read_sensor(sensorplugin):
    reading = {}
    reading["value"] = sensorplugin.getVal()
    reading["unit"] = sensorplugin.valUnit
    reading["symbol"] = sensorplugin.valSymbol
    reading["name"] = sensorplugin.valName
    reading["sensor"] = sensorplugin.sensorName
    reading["description"] = sensorplugin.description
    reading["readingType"] = sensorplugin.readingType
    return reading

def read_gps(sensorplugin):
    reading = {}
    val = i.getVal()
    LOGGER.debug("GPS output %s" % (val,))
    reading["latitude"] = val[0]
    reading["longitude"] = val[1]
    if not isnan(val[2]):
        reading["altitude"] = val[2]
    reading["disposition"] = val[3]
    reading["exposure"] = val[4]
    reading["name"] = i.valName
    reading["sensor"] = i.sensorName
    return reading

def sample():
    lastupdated = 0;
    while True:
        try:
            curTime = time.time()
            sampleTime = None
            if (curTime - lastupdated) > (settings['SAMPLEFREQ'] - 0.01):
                lastupdated = curTime
                data = []
                alreadySentSensorAlerts = False
                alreadySentOutputAlerts = False
                #Collect the data from each sensor
                sensorsworking = True
                for i in pluginsSensors:
                    datadict = {}
                    sampletime = datetime.now()
                    if i == gpsPluginInstance:
                        datadict = read_gps(i)
                    else:
                        datadict = read_sensor(i)
                        # TODO: Ensure this is robust
                        if datadict["value"] is None or isnan(float(datadict["value"])) or datadict["value"] == 0:
                            sensorsworking = False
                    data.append(datadict)
                # Record the outcome
                if sensorsworking:
                    LOGGER.info("Success: Data obtained from all sensors.")
                else:
                    if not alreadySentSensorAlerts:
                        for j in pluginsNotifications:
                            j.sendNotification("alertsensor")
                        alreadySentSensorAlerts = True
                    msg = "Error: Failed to obtain data from all sensors."
                    LOGGER.error(msg)
                    if settings['PRINTERRORS']:
                        print(msg)
                # Output data
                try:
                    outputsWorking = True
                    for i in pluginsOutputs:
                        if i.outputData(data) == False:
                            outputsWorking = False
                    # Record the outcome
                    if outputsWorking:
                        LOGGER.info("Success: Data output in all requested formats.")
                        if settings['GREENPIN'] and (settings['SUCCESSLED'] == "all" or (settings['SUCCESSLED'] == "first" and not greenHasLit)):
                            led_on(settings['GREENPIN'])
                            greenHasLit = True
                    else:
                        if not alreadySentOutputAlerts:
                            for j in pluginsNotifications:
                                j.sendNotification("alertoutput")
                            alreadySentOutputAlerts = True
                        msg = "Error: Failed to output in all requested formats."
                        LOGGER.error(msg)
                        if settings['PRINTERRORS']:
                            print(msg)
                        if settings['REDPIN'] and (settings['FAILLED'] in ["all", "constant"] or (settings['FAILLED'] == "first" and not redHasLit)):
                            led_on(settings['REDPIN'])
                            redHasLit = True
                except KeyboardInterrupt:
                    raise
                except Exception as excep:
                    LOGGER.error("Exception: %s" % excep)
                else:
                    # Delay before turning off LED
                    time.sleep(1)
                    if settings['GREENPIN']:
                        led_off(settings['GREENPIN'])
                    if settings['REDPIN'] and settings['FAILLED'] != "constant":
                        led_off(settings['REDPIN'])
            try:
                time.sleep(settings['SAMPLEFREQ'] - (time.time() - curTime))
            except KeyboardInterrupt:
                raise
            except Exception:
                pass # fall back on old method...
        except KeyboardInterrupt:
            interrupt_handler()

CFGPATHS = set_paths()

# Set up logging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.handlers.RotatingFileHandler(CFGPATHS['log'], maxBytes=40960, backupCount=5)
LOGGER.addHandler(HANDLER)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
# Uncomment below for logging output
#logging.basicConfig(level=logging.DEBUG)


#Set variables
gpsPluginInstance = None
metadata = None

#Set up plugins
pluginsSensors = set_up_sensors()
pluginsOutputs = set_up_outputs()
plugingsNotifications = set_up_notifications()
settings = set_settings()

greenHasLit = False
redHasLit = False

led_setup(settings['REDPIN'], settings['GREENPIN'])

# Register the signal handler
signal.signal(signal.SIGINT, interrupt_handler)

print("==========================================================")
print("Success: Setup complete.")

if metadata is not None:
    print("==========================================================")
    print(metadata)
    print("==========================================================")
    del metadata

delay_start(datetime.now())

sample()