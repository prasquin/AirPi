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
    """Exception to raise when an imported plugin is missing a required
    field.

    """
    pass

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
        boolean True if successfully connects to the site within five seconds.
        boolean False if fails to connect to the site within five seconds.

    """
    try:
        urllib2.urlopen("http://www.google.com", timeout=5)
        return True
    except urllib2.URLError as err:
        pass
    return False

def any_plugins_enabled(plugins, plugintype):
    """Warn user if no plugins in a list are enabled.

    Print and log a message if the list of enabled plugins is empty, i.e. there
    are no plugins enabled.

    Args:
        plugins: Array of plugins to check.
        type:    The type of plugin being checked.
    Returns:
        boolean True if there are any plugins enabled.

    """
    if not plugins:
        msg = "There are no " + plugintype + " plugins enabled!"
        msg += " Please enable at least one and try again."
        print(msg)
        LOGGER.error(msg)
        sys.exit(1)
    else:
        return True

def led_setup(redpin, greenpin):
    """Set up AirPi LEDs.

    Carry out initial setup of AirPi LEDs, including setting them to 'off'.

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

    Turn on an AirPi LED at a given GPIO pin number.

    Args:
        pin: Pin number of the LED to turn on.

    """
    GPIO.output(pin, GPIO.HIGH)

def led_off(pin):
    """Turn LED off.

    Turn off an AirPi LED at a given GPIO pin number.

    Args:
        pin: Pin number of the LED to turn off.

    """
    GPIO.output(pin, GPIO.LOW)

def get_serial():
    """Get Raspberry Pi serial no.

    Get the serial number of the Raspberry Pi.
    See: http://raspberrypi.nxez.com/2014/01/19/getting-your-raspberry-pi-serial-number-using-python.html

    Returns:
        string The serial number, or an error string.

    """
    cpuserial = "0000000000000000"
    try:
        thefile = open('/proc/cpuinfo', 'r')
        for line in thefile:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        thefile.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

def get_hostname():
    """Get current hostname.

    Get the current hostname of the Raspberry Pi.

    Returns:
        string The hostname.

    """
    if socket.gethostname().find('.')>=0:
        return socket.gethostname()
    else:
        return socket.gethostbyaddr(socket.gethostname())[0]

def set_cfg_paths():
    """Set paths to cfg files.

    Set the paths to config files. Assumes that they are in a sub-directory
    called 'cfg', within the same directory as the current script (airpi.py).

    Returns:
        dict The paths to the various config files.

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
    Log the file name if it does exist.

    Args:
        filetocheck: The file to check the existence of.

    Returns:
        boolean True if the file exists.

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
    enabled, then checking that all required fields are present in sensors.cfg.

    Returns:
        list A list containing the enabled 'sensor' objects.

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
                enabled = SENSORCONFIG.getboolean(i, "enabled")
                LOGGER.info(str(i) + " enabled status is: " + str(enabled))
            except Exception as excep:
                enabled = True

            #if enabled, load the plugin
            if enabled:

                try:
                    filename = SENSORCONFIG.get(i, "filename")
                    LOGGER.info("filename is " + filename)
                except Exception:
                    msg = "Error: no filename config option found for sensor"
                    msg += "plugin " + str(i)
                    print(msg)
                    LOGGER.error(msg)
                    raise

                try:
                    # 'a' means nothing below, but argument must be non-null
                    LOGGER.info("Trying to import sensors." + filename)
                    mod = __import__('sensors.' + filename, fromlist = ['a'])
                except Exception as excep:
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
                # Sensors don't have any common params, so this is empty
                common = []

                plugindata = define_plugin_params(SENSORCONFIG, i, reqd, opt, common)

                instclass = sensorclass(plugindata)
                # check for a getVal
                if callable(getattr(instclass, "getVal", None)):
                    sensorplugins.append(instclass)
                    # store sensorplugins array length for GPS plugin
                    if "serial_gps" in filename:
                        global gpsplugininstance
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
    should be enabled, then checking that all required fields are present in
    outputs.cfg.

    Returns:
        list A list containing the enabled 'output' objects.

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
                msg = "Error: no filename config option found for output"
                msg += " plugin " + str(i)
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
                    msg = "Error: could not find a subclass of output.Output"
                    msg += " in module " + filename
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
                # Output plugins don't have any common params so this is empty
                common = []
                
                plugindata = define_plugin_params(OUTPUTCONFIG, i, reqd, opt, common)

                if OUTPUTCONFIG.has_option(i, "needsinternet") and OUTPUTCONFIG.getboolean(i, "needsinternet") and not check_conn():
                    msg = "Error: Skipping output plugin " + i
                    msg += " because no internet connectivity."
                    print (msg)
                    LOGGER.info(msg)
                else:
                    instclass = outputclass(plugindata)
                    instclass.async = plugindata['async']
                    
                    # check for an output_data function
                    if callable(getattr(instclass, "output_data", None)):
                        outputplugins.append(instclass)
                        msg = "Success: Loaded output plugin " + str(i)
                        print(msg)
                        LOGGER.info(msg)
                        if "http" in str(instclass):
                            msg = "         Web data are (probably) at http://"
                            msg += instclass.get_ip() + ":8080"
                            print(msg)
                            # TODO: Make the above get the port number as well - don't just assume 8080
                        if "dweet" in str(instclass):
                            msg = "         dweeting to " + instclass.get_url()
                            print(msg)
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

def define_plugin_params(config, name, reqd, opt, common):
    """Define setup parameters for an plugin.

    Take a list of parameters supplied by the user ('config'), and compare to
    the separate lists of 'required', 'optional' and 'common' parameters for the
    plugin. Check that 'required' ones are present (raise a MissingField
    exception if not). Merge all three dicts into one 'params' dict that holds
    all setup parameters for this plugin, then tag metadata and async info on to
    the end.
    Parameters supplied by the user usually come from the relevant cfg file,
    while the lists of 'required', 'optional' and 'common' parameters are
    normally defined in the plugin Class.

    Args:
        outputconfig: The configparser containing the parameters defined by
                      the user.
        outputname: The name of the plugin defined in the config file.
        reqd: List of parameters required by the plugin.
        opt: List of parameters considered optional for the plugin.
        common: List of parameters which are common across all plugins.

    Returns:
        dict A dict containing the various parameters.

    """
    params = {}
    for reqdfield in reqd:
        if config.has_option(name, reqdfield):
            params[reqdfield] = config.get(name, reqdfield)
        else:
            msg = "Error: Missing required field '" + reqdfield
            msg += "' for plugin " + name + "." + os.linesep
            msg += "Error: This should be found in file: "
            msg += CFGPATHS['outputs']
            print(msg)
            LOGGER.error(msg)
            raise MissingField
    for optfield in opt:
        if config.has_option(name, optfield):
            params[optfield] = config.get(name, optfield)
    for commonfield in common:
        if config.has_option("Common", commonfield):
            params[commonfield] = config.get("Common", commonfield)

    # Only applies to output plugins
    if config.has_option(name, "metadatareqd") and config.getboolean(name, "metadatareqd"):
        params['metadatareqd'] = True
    else:
        params['metadatareqd'] = False

    if config.has_option(name, "async"):
        params['async'] = config.getboolean(name, "async")
    else:
        params['async'] = False

    return params

def set_up_notifications():
    """Set up AirPi notification plugins.

    Set up AirPi notification plugins by reading notifications.cfg to determine
    which should be enabled. For each plugin, check that all required fields
    are present; if so, create an instance of the plugin class and append it to
    the list of Notification plugins. Return the list.

    Returns:
        list A list containing the enabled 'notification' objects.

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
                msg = "Error: no filename config option found for notification"
                msg += " plugin " + str(i)
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
                    msg = "Error: could not find a subclass of"
                    msg += " notification.Notification in module " + filename
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

                plugindata = define_plugin_params(NOTIFICATIONCONFIG, i, reqd, opt, common)
                
                if NOTIFICATIONCONFIG.has_option(i, "needsinternet"):
                    if NOTIFICATIONCONFIG.getboolean(i, "needsinternet") and not check_conn():
                        msg = "Error: Skipping notification plugin " + i
                        msg += " because no internet connectivity."
                        print (msg)
                        LOGGER.info(msg)
                    else:
                        instclass = notificationclass(plugindata)
                        instclass.async = plugindata['async']

                    # check for a sendNotification function
                    if callable(getattr(instclass, "sendNotification", None)):
                        notificationPlugins.append(instclass)
                        msg = "Success: Loaded notification plugin " + str(i)
                        print(msg)
                        LOGGER.info(msg)
                    else:
                        msg = "Error: no callable sendNotification() function"
                        msg += " for notification plugin " + str(i)
                        print(msg)
                        LOGGER.info(msg)

        except Exception as excep:
            msg = "Error: Did not import notification plugin " + str(i) + ": "
            msg += str(excep)
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
        list A list containing the various settings.

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
    settingslist['STOPAFTER'] = mainconfig.getint("Sampling", "stopafter")
    settingslist['REDPIN'] = mainconfig.getint("LEDs", "redPin")
    settingslist['GREENPIN'] = mainconfig.getint("LEDs", "greenPin")
    settingslist['SUCCESSLED'] = mainconfig.get("LEDs","successLED")
    settingslist['FAILLED'] = mainconfig.get("LEDs","failLED")
    settingslist['OPERATOR'] = mainconfig.get("Misc", "operator")
    settingslist['PRINTERRORS'] = mainconfig.getboolean("Misc","printErrors")
    settingslist['WAITTOSTART'] = mainconfig.getboolean("Debug","waittostart")

    print("Success: Loaded settings.")

    return settingslist

def set_metadata():
    """Set metadata.

    Set up metadata for this run. Outputting of the metadata is handled by each
    of the output plugins individually, so that you can - for example - output
    metadata via Print and CSVOutput in the same run.

    Returns:
        dict All metadata elements.

    """
    meta = {
        "STARTTIME":time.strftime("%H:%M on %A %d %B %Y"),
        "OPERATOR":settings['OPERATOR'],
        "PIID":get_serial(),
        "PINAME":get_hostname(),
        "SAMPLEFREQ":"Sampling every " + str(int(settings['SAMPLEFREQ'])) + " seconds.",
        "STOPAFTER":str(int(settings['STOPAFTER'])) + " samples."
        }
    if settings['AVERAGE']:
        meta['AVERAGEFREQ'] = "Averaging every " + str(settings['AVERAGEFREQ'])
        meta['AVERAGEFREQ'] += " seconds."
    return meta

def output_metadata(plugins, meta):
    """Output metadata via enabled plugins.

    Output metadata for the run via each of the enabled 'output' plugins. Note
    that some output plugins will not output metadata as it is not appropriate.

    Args:
        plugins: List of enabled 'output' plugins.
        meta: Metadata for the run.

    """
    if meta is None:
        meta = self.set_metadata()
    for plugin in plugins:
        plugin.output_metadata(meta)

def delay_start(timenow):
    """Delay sampling until start of the next minute.

    Prevent sampling until the start of the next minute (i.e. 0 seconds) by
    sleeping from 'timenow' until then in 10-second chunks. Print a message to
    the user first, and then every 10 seconds.

    Args:
        timenow: Time from which the delay should begin.

    """
    SECONDS = float(timenow.second + (timenow.microsecond / 1000000))
    DELAY = (60 - SECONDS)
    if DELAY != 60:
        print("==========================================================")
        print("Info: Sampling will start in " + str(int(DELAY)) + " seconds.")
        remainder = DELAY % 10
        remaining = DELAY - remainder
        time.sleep(remainder)
        while remaining >= 1:
            msg = "Info: Sampling will start in " + str(int(remaining))
            msg += " seconds."
            print(msg)
            time.sleep(10)
            remaining -= 10

def read_sensor(sensorplugin):
    """Read from a non-GPS sensor.

    Read info from a sensor. Note this is not just the value, but also the
    sensor name, units, symbol, etc. N.B. GPS data is read using `read_gps()`.

    Args:
        sensorplugin: The sensor plugin which should be read.

    Returns:
        dict The sensor data.

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

    Read info from a GPS sensor. Note this is not just one value, but multiple
    values for latitude, longitude, etc. N.B. Non-GPS data is read using
    `read_sensor()`.

    Args:
        sensorplugin: The sensor plugin which should be read.

    Returns:
        dict All of the sensor data elements.

    """
    reading = {}
    val = sensorplugin.getVal()
    LOGGER.debug("GPS output %s" % (val,))
    reading["latitude"] = val[0]
    reading["longitude"] = val[1]
    if not isnan(val[2]):
        reading["altitude"] = val[2]
    reading["disposition"] = val[3]
    reading["exposure"] = val[4]
    reading["name"] = sensorplugin.valName
    reading["sensor"] = sensorplugin.sensorName
    return reading

def sample():
    """Sample from sensors and record the output.

    Commence and then continue sampling from the enabled sensors and writing
    to enabled 'output' plugins. Will continue until forceably stopped with
    Ctrl+C.

    """

    print("Info: Starting sampling...")
    print("==========================================================")
    lastupdated = 0
    alreadysentsensornotifications = False
    alreadysentoutputnotifications = False
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
                    # Always record raw values for every sensor
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
                            LOGGER.debug("This is the dataset to be output to " + str(i) + " :")
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
                                    False
                                    #j.sendNotification("alertoutput")
                                alreadysentoutputnotifications = True
                            msg = "Error: Failed to output in all requested"
                            msg += " formats."
                            LOGGER.error(msg)
                            if settings['PRINTERRORS']:
                                print(msg)
                            if settings['REDPIN'] and (settings['FAILLED'] in ["all", "constant"] or (settings['FAILLED'] == "first" and not redhaslit)):
                                led_on(settings['REDPIN'])
                                redhaslit = True

                except KeyboardInterrupt:
                    raise
                except Exception as excep:
                    LOGGER.error("Exception during output: %s" % excep)
                else:
                    # Delay before turning off LED
                    time.sleep(1)
                    if settings['GREENPIN']:
                        led_off(settings['GREENPIN'])
                    if settings['REDPIN'] and settings['FAILLED'] != "constant":
                        led_off(settings['REDPIN'])
            global samples
            samples += 1
            if samples == settings['STOPAFTER'] and samples != 0:
                print("[AirPi] Reached requested number of samples - stopping run.")
                stop_sampling(None, None)
            try:
                time.sleep(settings['SAMPLEFREQ'] - (time.time() - curtime))
            except KeyboardInterrupt:
                raise
            except Exception:
                pass # fall back on old method...
        except KeyboardInterrupt:
            stop_sampling()

def average_dataset(identifier, dataset):
    """Average a dataset.

    Take a dataset consisting of 'n' separate readings, and calculate
    the mean across those readings. The dataset will be a dict of dicts; each
    element in the first dict is a single time point in the set to be averaged.
    Each of these single time points is a dict which contains one reading for
    each of the enabled sensors.

    Args:
        identifier: The unique identifier for the sensor and property being
            averaged.
        dataset: The list of 'n' separate time points to be averaged.

    Returns:
        list The averaged data.

    """
    totals = {}
    avgs = {}
    numberofsamples = {}
    # For each identifier, sum the indidivual values in the
    # dataset[identifier]['values'] list.
    # Count the number of samples as we go along, in case one sensor has missed
    # any readings.
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

def stop_sampling(signal, frame):
    """Stop a run.

    Stop a run by shutting down the GPS controller, turning off LEDs and then
    printing a summary of the run statistics. Note that this can be run either
    programatically because we have completed the requested number of samples,
    or manually because the user pressed Ctrl+C.

    """
    print(os.linesep)
    print("[AirPi] Sampling stopping...")
    if gpsplugininstance:
        gpsplugininstance.stopController()
    led_off(settings['GREENPIN'])
    led_off(settings['REDPIN'])
    timedelta = datetime.utcnow() - starttime
    hours, remainder = divmod(timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print("[AirPi] This run lasted " + str(hours) + "h"),
    print(str(minutes) + "m " + str(seconds)  + "s,"),
    print("and consisted of " + str(samples) + " samples.")
    print("[AirPi] Sampling stopped.")
    sys.exit(1)

if __name__ == '__main__':
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
    settings = set_settings()
    notificationsMade = {}
    samples = 0
    starttime = datetime.utcnow()

    #Set up plugins
    pluginssensors = set_up_sensors()
    pluginsoutputs = set_up_outputs()
    pluginsnotifications = set_up_notifications()

    # Set up metadata
    METADATA = set_metadata()
    if any_plugins_enabled(pluginsoutputs, 'output'):
        output_metadata(pluginsoutputs, METADATA)

    #Set up LEDs
    greenhaslit = False
    redhaslit = False
    led_setup(settings['REDPIN'], settings['GREENPIN'])

    # Register the Ctrl+C signal handler
    signal.signal(signal.SIGINT, stop_sampling)

    print("==========================================================")
    print("Info: Success - setup complete.")

    # Wait until the start of the next minute
    if settings["WAITTOSTART"]:
        delay_start(datetime.now())

    # Sample!
    sample()