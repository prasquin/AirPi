#!/usr/bin/env python

"""Start sampling with an AirPi board.

This is the main script file for sampling air quality and/or weather
data with an AirPi board on a Raspberry Pi. It takes configuration
settings from a number of config files, and outputs data from the specified
sensors in one or more requested formats. Errors notifications can be raised
via several methods.

See: http://airpi.es
     http://github.com/haydnw/airpi

"""

import sys
sys.dont_write_bytecode = True

import socket
import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os
import signal
import urllib2
import logging
from logging import handlers
from datetime import datetime
from math import isnan
from sensors import sensor
from outputs import output
from notifications import notification

class MissingField(Exception):
    """Exception to raise when an imported plugin is missing a required field."""
    pass

def interrupt_handler(signal, frame):
    """Handle the Ctrl+C KeyboardInterrupt by exiting."""
    if gpsplugininstance:
        gpsplugininstance.stopController()
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

def any_plugins_enabled(plugins, type):
    """Warn user if no plugins in a list are enabled.

    Print and log a message if a plugin list doesn't
    actually contain any loaded plugins.

    Args:
        plugins: Array of plugins to check.
        type:    The type of plugin being checked.
    Returns:
        True if there are any plugins enabled.

    """
    if not plugins:
        msg = "There are no " + type + " plugins enabled! Please enable at least one and try again."
        print(msg)
        LOGGER.error(msg)
        sys.exit(1)
    else:
        return True

def led_setup(redpin, greenpin):
    """Set up AirPi LEDs.

    Carry out initial setup of AirPi LEDs.

    Args:
        redpin:   GPIO pin number for red pin.
        greenpin: GPIO pin number for green pin.

    """
    if redpin:
        GPIO.setup(redpin, GPIO.OUT, initial=GPIO.LOW)
    if redpin:
        GPIO.setup(greenpin, GPIO.OUT, initial=GPIO.LOW)

def led_on(pin):
    """Turn LED on.

    Turn on an AirPi LED.

    Args:
        pin: Pin number of the LED to turn on.

    """
    GPIO.output(pin, GPIO.HIGH)

def led_off(pin):
    """Turn LED off.

    Turn off an AirPi LED.

    Args:
        pin: Pin number of the LED to turn off.

    """
    GPIO.output(pin, GPIO.LOW)

def getserial():
    """Get Raspberry Pi serial no.

    Get the serial number of the Raspberry Pi.
    See: http://raspberrypi.nxez.com/2014/01/19/getting-your-raspberry-pi-serial-number-using-python.html

    Returns:
        True if there are any plugins enabled.

    """
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

def gethostname():
    """Get current hostname.

    Get the current hostname of the Raspberry Pi.

    Returns:
        The hostname.

    """
    if socket.gethostname().find('.')>=0:
        host = socket.gethostname()
    else:
        host = socket.gethostbyaddr(socket.gethostname())[0]
    return host

def set_cfg_paths():
    """Set paths to cfg files.

    Set the paths to config files. Assumes that they are in a sub-directory
    called 'cfg', within the same directory as the current script (airpi.py).

    Returns:
        Dict containing paths to the various config files.

    """
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
    """Check cfg file exists.

    Check whether a specified cfg file exists. Print and log a warning if not.
    Print and log the file name if it does exist.

    Args:
        filetocheck: The file to check the existence of.

    Returns:
        True if the file exists.

    """
    if not os.path.isfile(filetocheck):
        msg = "Unable to access config file: " + filetocheck
        print(msg)
        LOGGER.error(msg)
        exit(1)
    else:
        msg = "Config file: " + filetocheck
        LOGGER.info(msg)
        return True

def set_up_sensors():
    """Set up AirPi sensors.

    Set up AirPi sensors by reading sensors.cfg to determine which should be
    enabled, then checking that all required fields are present.

    Returns:
        List containing the enabled 'sensor' objects.

    """

    print("==========================================================")
    print("Loading SENSORS...")

    check_cfg_file(CFGPATHS['sensors'])

    SENSORCONFIG = ConfigParser.SafeConfigParser()
    SENSORCONFIG.read(CFGPATHS['sensors'])

    SENSORNAMES = SENSORCONFIG.sections()

    sensorplugins = []

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
                    sensorclass = get_subclasses(mod, sensor.Sensor)
                    if sensorclass == None:
                        raise AttributeError
                except Exception:
                    msg = "Error: could not find a subclass of sensor.Sensor"
                    msg += " in module " + filename
                    print(msg)
                    LOGGER.error(msg)
                    raise

                try:
                    reqd = sensorclass.requiredData
                except Exception:
                    reqd = []
                try:
                    opt = sensorclass.optionalData
                except Exception:
                    opt = []

                plugindata = {}

                for reqdfield in reqd:
                    if SENSORCONFIG.has_option(i, reqdfield):
                        plugindata[reqdfield] = SENSORCONFIG.get(i, reqdfield)
                    else:
                        msg = "Error: Missing required field '" + reqdfield
                        msg += "' for sensor plugin " + i + "." + os.linesep
                        msg += "Error: This should be found in file: " + CFGPATHS['sensors']
                        print(msg)
                        LOGGER.error(msg)
                        raise MissingField
                for optfield in opt:
                    if SENSORCONFIG.has_option(i, optfield):
                        plugindata[optfield] = SENSORCONFIG.get(i, optfield)
                instclass = sensorclass(plugindata)
                # check for a getVal
                if callable(getattr(instclass, "getVal", None)):
                    sensorplugins.append(instclass)
                    # store sensorplugins array length for GPS plugin
                    if i == "GPS":
                        gpsplugininstance = instclass
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

    if any_plugins_enabled(sensorplugins, 'sensor'):
        return sensorplugins

def set_up_outputs():
    """Set up AirPi output plugins.

    Set up AirPi output plugins by reading outputs.cfg to determine which
    should be enabled, then checking that all required fields are present.

    Returns:
        List containing the enabled 'output' objects.

    """

    print("==========================================================")
    print("Loading OUTPUTS...")

    check_cfg_file(CFGPATHS['outputs'])

    OUTPUTCONFIG = ConfigParser.SafeConfigParser()
    OUTPUTCONFIG.read(CFGPATHS['outputs'])

    OUTPUTNAMES = OUTPUTCONFIG.sections()

    outputplugins = []

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
                    outputclass = get_subclasses(mod, output.Output)
                    if outputclass == None:
                        raise AttributeError
                except Exception:
                    msg = "Error: could not find a subclass of output.Output in module " + filename
                    print(msg)
                    LOGGER.error(msg)
                    raise

                try:
                    reqd = outputclass.requiredParams
                except Exception:
                    reqd = []
                try:
                    opt = outputclass.optionalParams
                except Exception:
                    opt = []
                
                plugindata = {}
                for reqdfield in reqd:
                    if OUTPUTCONFIG.has_option(i, reqdfield):
                        plugindata[reqdfield] = OUTPUTCONFIG.get(i, reqdfield)
                    else:
                        msg = "Error: Missing required field '" + reqdfield
                        msg += "' for output plugin " + i + "." + os.linesep
                        msg += "Error: This should be found in file: " + CFGPATHS['outputs']
                        print(msg)
                        LOGGER.error(msg)
                        raise MissingField
                for optfield in opt:
                    if OUTPUTCONFIG.has_option(i, optfield):
                        plugindata[optfield] = OUTPUTCONFIG.get(i, optfield)

                if OUTPUTCONFIG.has_option(i, "metadatareqd") and OUTPUTCONFIG.getboolean(i, "metadatareqd"):
                    plugindata['metadatareqd'] = True
                else:
                    plugindata['metadatareqd'] = False

                if OUTPUTCONFIG.has_option(i, "async"):
                    async = OUTPUTCONFIG.getboolean(i, "async")
                else:
                    async = False

                if OUTPUTCONFIG.has_option(i, "needsinternet") and OUTPUTCONFIG.getboolean(i, "needsinternet") and not check_conn():
                        msg = "Error: Skipping output plugin " + i + " because no internet connectivity."
                        print (msg)
                        LOGGER.info(msg)
                else:
                    instclass = outputclass(plugindata)
                    instclass.async = async
                    
                    # check for an output_data function
                    if callable(getattr(instclass, "output_data", None)):
                        outputplugins.append(instclass)
                        msg = "Success: Loaded output plugin " + str(i)
                        print(msg)
                        LOGGER.info(msg)
                    else:
                        msg = "Success: Loaded support plugin " + str(i)
                        print(msg) 
                        LOGGER.info(msg)

        except Exception as excep: #add specific exception for missing module
            msg = "Error: Did not import output plugin " + str(i) + ": " + str(excep)
            print(msg)
            LOGGER.error(msg)
            raise excep

    if any_plugins_enabled(outputplugins, 'output'):
        return outputplugins

def set_up_notifications():
    """Set up AirPi notification plugins.

    Set up AirPi notification plugins by reading notifications.cfg to
    determine which should be enabled, then checking that all required
    fields are present.

    Returns:
        List containing the enabled 'notification' objects.

    """

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
                    notificationclass = get_subclasses(mod, notification.Notification)
                    if notificationclass == None:
                        raise AttributeError
                except Exception:
                    msg = "Error: could not find a subclass of notification.Notification in module " + filename
                    print(msg)
                    LOGGER.error(msg)
                    raise
                try:
                    reqd = notificationclass.requiredParams
                except Exception:
                    reqd = []
                try:
                    opt = notificationclass.optionalParams
                except Exception:
                    opt = []
                try:
                    common = notificationclass.commonParams
                except Exception:
                    common = []

                if NOTIFICATIONCONFIG.has_option(i, "async"):
                    async = NOTIFICATIONCONFIG.getboolean(i, "async")
                else:
                    async = False

                plugindata = {}

                for reqdfield in reqd:
                    if NOTIFICATIONCONFIG.has_option(i, reqdfield):
                        plugindata[reqdfield] = NOTIFICATIONCONFIG.get(i, reqdfield)
                    else:
                        msg = "Error: Missing required field '" + reqdfield
                        msg += "' for notification plugin " + i + "." + os.linesep
                        msg += "Error: This should be found in file: " + CFGPATHS['notifications']
                        print(msg)
                        LOGGER.error(msg)
                        raise MissingField

                for optfield in opt:
                    if NOTIFICATIONCONFIG.has_option(i, optfield):
                        plugindata[optfield] = NOTIFICATIONCONFIG.get(i, optfield)

                for commonfield in common:
                    if NOTIFICATIONCONFIG.has_option("Common", commonfield):
                        plugindata[commonfield] = NOTIFICATIONCONFIG.get("Common", commonfield)
                
                if NOTIFICATIONCONFIG.has_option(i, "needsinternet"):
                    if NOTIFICATIONCONFIG.getboolean(i, "needsinternet") and not check_conn():
                        msg = "Error: Skipping notification plugin " + i + " because no internet connectivity."
                        print (msg)
                        LOGGER.info(msg)
                    else:
                        instclass = notificationclass(plugindata)
                        instclass.async = async

                    # check for a sendNotification function
                    if callable(getattr(instclass, "sendNotification", None)):
                        notificationPlugins.append(instclass)
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

    # Don't run any_plugins_enabled here, because it's OK to not have any notifications
    if not notificationPlugins:
        msg = "Info: No Notifications enabled."
        print(msg)
        LOGGER.info(msg)
    return notificationPlugins

def set_settings():
    """Set up settings.

    Set up settings by reading from settings.cfg.

    Returns:
        List containing the various settings.

    """

    print("==========================================================")
    print("Loading SETTINGS...")

    check_cfg_file(CFGPATHS['settings'])
    mainconfig = ConfigParser.SafeConfigParser()
    mainconfig.read(CFGPATHS['settings'])
    settingslist = {}

    settingslist['AVERAGE'] = False
    settingslist['SAMPLEFREQ'] = mainconfig.getfloat("Sampling", "sampleFreq")
    settingslist['AVERAGEFREQ'] = mainconfig.getint("Sampling", "averageFreq")
    averagefreq = settingslist['AVERAGEFREQ']
    if averagefreq > 0:
        averagecount = averagefreq / settingslist['SAMPLEFREQ']
        if averagecount < 2:
            msg = "Error: averageFreq must be a least twice sampleFreq."
            print(msg)
            LOGGER.error(msg)
            sys.exit(1)
        else:
            settingslist['AVERAGE'] = True
            settingslist['AVERAGECOUNT'] = averagecount
            settingslist['PRINTUNAVERAGED'] = mainconfig.getboolean("Sampling", "printUnaveraged")
    settingslist['REDPIN'] = mainconfig.getint("LEDs", "redPin")
    settingslist['GREENPIN'] = mainconfig.getint("LEDs", "greenPin")
    settingslist['SUCCESSLED'] = mainconfig.get("LEDs","successLED")
    settingslist['FAILLED'] = mainconfig.get("LEDs","failLED")
    settingslist['OPERATOR'] = mainconfig.get("Misc", "operator")
    settingslist['PRINTERRORS'] = mainconfig.getboolean("Misc","printErrors")

    print("Success: Loaded settings.")

    return settingslist

def set_metadata():
    """Set metadata.

    Set up metadata for this run.

    Returns:
        Dict containing all metadata.

    """
    meta = {
        "STARTTIME":time.strftime("%H:%M on %A %d %B %Y"),
        "OPERATOR":settings['OPERATOR'],
        "PIID":getserial(),
        "PINAME":getHostname(),
        "SAMPLEFREQ":"Sampling every " + str(int(settings['SAMPLEFREQ'])) + " seconds."
        }
    if settings['AVERAGE']:
        meta['AVERAGEFREQ'] = "Averaging every " + str(settings['AVERAGEFREQ']) + " seconds."
    return meta

def output_metadata(plugins, meta):
    """Output metadata via enabled plugins.

    Output metadata for the run via all enabled 'output' plugins.

    Args:
        plugins: List of enabled 'output' plugins.
        meta: Metadata for the run.

    """
    for plugin in plugins:
        plugin.output_metadata(meta)

def delay_start(timenow):
    """Delay sampling until start of the next minute.

    Prevent sampling until the start of the next minute (i.e. 0 seconds)
    by sleeping from 'timenow' until then. Print a message to the user
    first.

    Args:
        timenow: Time from which the delay should begin.

    """
    SECONDS = float(timenow.second + (timenow.microsecond / 1000000))
    DELAY = (60 - SECONDS)
    if DELAY != 60:
        print("==========================================================")
        print("Info: Sampling will start in " + str(int(DELAY)) + " seconds...")
        print("==========================================================")
        time.sleep(DELAY)

def read_sensor(sensorplugin):
    """Read from a non-GPS sensor.

    Read info from a sensor. Note this is not just the value, but also
    the sensor name, units, symbol etc.
    N.B. GPS data is read using `read_gps`.

    Args:
        sensorplugin: The sensor plugin which should be read.

    Returns:
        Dict containing the sensor data.

    """
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
    """Read from a GPS sensor.

    Read info from a GPS sensor. Note this is not just the value, but also
    the sensor name, units, symbol etc.
    N.B. Non-GPS data is read using `read_sensor`.

    Args:
        sensorplugin: The sensor plugin which should be read.

    Returns:
        Dict containing the sensor data.

    """
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
    """Sample from sensors and record output.

    Commence and continue sampling from the enabled sensors and writing
    to enabled 'output' plugins. Will continue until forceably stopped
    with Ctrl+C.

    """
    lastupdated = 0;
    if settings['AVERAGE']:
        countcurrent = 0
        counttarget = settings['AVERAGECOUNT']
        dataset = {}
    while True:
        try:
            curtime = time.time()
            sampletime = None
            if (curtime - lastupdated) > (settings['SAMPLEFREQ'] - 0.01):
                lastupdated = curtime
                data = []
                alreadysentsensornotifications = False
                alreadysentoutputnotifications = False
                # Read the sensors
                sensorsworking = True
                for i in pluginssensors:
                    datadict = {}
                    sampletime = datetime.now()
                    if i == gpsplugininstance:
                        datadict = read_gps(i)
                    else:
                        datadict = read_sensor(i)
                        # TODO: Ensure this is robust
                        if datadict["value"] is None or isnan(float(datadict["value"])) or datadict["value"] == 0:
                            sensorsworking = False
                    # Average the data if required
                    if settings['AVERAGE'] and i != gpsplugininstance:
                        identifier = datadict['sensor'] + "-" + datadict['name']
                        if identifier not in dataset:
                            dataset[identifier] = {}
                            temp = datadict.copy()
                            temp.pop("value", None)
                            for thekey, thevalue in temp.iteritems():
                                if thekey not in dataset[identifier]:
                                    dataset[identifier][thekey] = thevalue
                            dataset[identifier]['values'] = []
                        dataset[identifier]['values'].append(datadict["value"])
                    # Always record raw values
                    data.append(datadict)
                # Record the outcome of reading sensors
                if settings['AVERAGE']:
                    countcurrent += 1
                if sensorsworking:
                    LOGGER.info("Success: Data obtained from all sensors.")
                else:
                    if not alreadysentsensornotifications:
                        for j in pluginsnotifications:
                            j.sendNotification("alertsensor")
                        alreadysentsensornotifications = True
                    msg = "Error: Failed to obtain data from all sensors."
                    LOGGER.error(msg)
                    if settings['PRINTERRORS']:
                        print(msg)
                # Output data
                try:
                    # Averaging
                    if settings['AVERAGE']:
                        if countcurrent == counttarget:
                            data = average_dataset(identifier, dataset)
                            dataset = {}
                    if (settings['AVERAGE'] and countcurrent == counttarget) or (settings['AVERAGE'] == False):
                        if settings['AVERAGE']:
                            countcurrent = 0
                        # Output the data
                        outputsworking = True
                        for i in pluginsoutputs:
                            LOGGER.debug(data)
                            if i.output_data(data) == False:
                                outputsworking = False
                        # Record the outcome of outputting data
                        if outputsworking:
                            LOGGER.info("Success: Data output in all requested formats.")
                            if settings['GREENPIN'] and (settings['SUCCESSLED'] == "all" or (settings['SUCCESSLED'] == "first" and not greenhaslit)):
                                led_on(settings['GREENPIN'])
                                greenhaslit = True
                        else:
                            if not alreadysentoutputnotifications:
                                for j in pluginsnotifications:
                                    j.sendNotification("alertoutput")
                                alreadysentoutputnotifications = True
                            msg = "Error: Failed to output in all requested formats."
                            LOGGER.error(msg)
                            if settings['PRINTERRORS']:
                                print(msg)
                            if settings['REDPIN'] and (settings['FAILLED'] in ["all", "constant"] or (settings['FAILLED'] == "first" and not redhaslit)):
                                led_on(settings['REDPIN'])
                                redhaslit = True

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
                time.sleep(settings['SAMPLEFREQ'] - (time.time() - curtime))
            except KeyboardInterrupt:
                raise
            except Exception:
                pass # fall back on old method...
        except KeyboardInterrupt:
            interrupt_handler()

def average_dataset(identifier, dataset):
    """Average a dataset.

    Take a dataset consisting of 'n' separate readings, and calculate
    the mean across those readings.

    Args:
        identifier: The unique identifier for the sensor and parameter
            being averaged.
        dataset: The list of 'n' separate readings to be averaged.

    Returns:
        List containing the averaged data.

    """
    totals = {}
    avgs = {}
    numberofsamples = {}
    # For each identifier, sum the indidivual values in the dataset[identifier]['values'] list
    # Count the number of samples as we go along, in case one sensor has missed any readings
    for identifier, properties in dataset.iteritems():
        totals[identifier] = 0
        numberofsamples[identifier] = 0
        for value in properties['values']:
            if value != "-" and value is not None and not isnan(value):
                totals[identifier] += value
                numberofsamples[identifier] += 1
    # For each identifier, divide the sum by the number of samples
    for identifier, total in totals.iteritems():
        dataset[identifier]['value'] = total / numberofsamples[identifier]
        dataset[identifier]['readingType'] = "average"
    # Re-format to that expected by output_data methods of output plugins
    formatted = []
    for identifier in dataset:
        dataset[identifier]['identifier'] = identifier
        formatted.append(dataset[identifier])
    return formatted

def main():
    """Execute a run.

    Set up and execute an AirPi sampling run.

    """

    CFGPATHS = set_cfg_paths()

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
    gpsplugininstance = None

    #Set up plugins
    pluginssensors = set_up_sensors()
    pluginsoutputs = set_up_outputs()
    pluginsnotifications = set_up_notifications()
    settings = set_settings()

    METADATA = set_metadata()
    if any_plugins_enabled(pluginsoutputs, 'output'):
        output_metadata(pluginsoutputs, METADATA)

    greenhaslit = False
    redhaslit = False
    led_setup(settings['REDPIN'], settings['GREENPIN'])

    # Register the signal handler
    signal.signal(signal.SIGINT, interrupt_handler)

    print("==========================================================")
    print("Success: Setup complete.")

    delay_start(datetime.now())

    sample()

if __name__ == '__main__':
    main()