# =============================================================================
# File:     useage.md
# Purpose:  Instructions for using AirPi software.
# Author:   Haydn Williams <pi@hwmail.co.uk>
# Date:     December 2015
# =============================================================================

# AirPi Software Usage Instructions

## About
This fork of the AirPi software is held on GitHub at http://github.com/haydnw/AirPi

This document assumes that the software has been installed in the default location,
which is /home/pi/AirPi and that you have added that directory to your $PATH variable;
this can be done by adding the following line to ~/.profile:
```shell
PATH="/home/pi/AirPi:$PATH"
```

## Starting and Stopping Sampling
The software is controlled using the script named 'airpictl.sh'. It has three
sampling modes, to deal with various situations. The sampling mode should be
chosen based on whether you need to do anything else while logged in to the
Raspberry Pi, and whether you are logged in directly or via SSH. The three
sampling modes are:
**normal** - Runs in the foreground; you cannot do anything else while the sampling
is under way.
**bg** - Runs in the background while you are logged in. You can do other things
and the sampling will continue as long as you are logged in. If you log out, the
sampling will stop.
**unatt** - Runs unattended in the background even if you log out. You can do other things while
logged in, and you even can log out and then back in again later. The sampling
will only stop if you specifically request it to.

To start sampling, run the script and append the sampling mode after it:
```shell
airpictl.sh normal
```

To stop sampling, either press Ctrl+C when running in 'normal' mode, or use
the airpictl.sh script to stop background or unattended runs:
```shell
airpictl.sh stop
```

## Settings
Settings are defined in the settings.cfg file, which can be found in the cfg
directory. Values do not need any quote marks around them. Strings may include
spaces. There is equivalence between yes/on/true and between no/off/false; these
are not case-sensitive. Comments take an entire line, and begin with a hash.

There are a number of sections within the file:

**Sampling** controls the frequency and duration of the sampling, and features
relating to the collection of average data rather than point data.
+ *sampleFreq* specifies how often readings should be taken (in seconds). It is
recommended that you do not specify a duration of less than five seconds, as
unpredictable behaviour may result.
+ *stopafter* allows you to stop sampling after the specified number of samples
have been taken. Remember that you have used *sampleFreq* to determine the time
between samples, so this effectively allows you to stop sampling after a certain
time period too. Set this to 0 (zero) to continue indefinitely.
+ *averageFreq* specifies how often, in seconds, an average reading should be
calculated from point readings. For example, if *sampleFreq* is set to 10 and
*averageFreq* is set to 30, the system will average three point readings to
produce a single averaged reading every 30 seconds. Set this to 0 (zero) to
disable averaging.
+ *dummyduration* specifies how long, in seconds, the system should obtain
sensor readings *without recording them* ('dummy' runs). This allows you initialise the system
prior to recording data. Set this to 0 (zero) to disable initialising 'dummy'
runs.
+ *printUnaveraged* is not used at present.


**LEDs** controls the behaviour of the red and green LEDs on the AirPi (*N.B.*
not the Raspberry Pi LEDs).
*redPin* specifies the wiring pin used for the red LED.
*greenPin* specifies the wiring pin used for the green LED.
*successLED* specifies the behaviour of the green LED. Setting this to 'all' will
flash the green AirPi LED each time a successful sample is taken (no errors).
Setting this to 'first' will flash the green AirPi LED when the first successful
sample is taken, but then there will be no further flashes.
*failLED* specifies the behaviour of the red LED. Setting this to 'all' will
flash the red AirPi LED each time a failed sample is taken (one or more errors).
Setting this to 'first' will flash the red AirPi LED when the first failed
sample is taken, but then there will be no further flashes. Setting this to
'constant' will light the red AirPi LED when the first failed sample is taken
(one or more errors) and will remain lit until the sampling is stopped.

**Misc** controls a number of other settings.
*printErrors* specifies whether or not error messages should be printed to screen.
If enabled, you may find that error messages are printed in amongst screen output
from your enabled output plugins.
*bootstart* specifies whether the AirPi should start automatically sampling as
soon as it boots up. See the 'boot' folder for more information.
*operator* specifies the name of the operator who is running the AirPi sampling.
This information is included in output if metadata is requested.
*help* determines whether extra text should be printed during sampling to provide
further helpful information about the run.

**Debug** is only likely to be useful if you experience any problems with the
software, or do your own development of it.
*debug* specifies whether 'debug mode' should be active; if so, many diagnostic
messages will be printed to screen during a run.
*waittostart* specifies whether sampling will be delayed until the 'start' of a
minute, *i.e.* zero seconds. It can be useful to turn this off to save time when
debugging.


## Sensors
Sensors are defined in the sensors.cfg file, which can be found in the cfg
directory. Values do not need any quote marks around them. Strings may include
spaces (except for *sensorName* and *measurement*). There is equivalence between
yes/on/true and between no/off/false; these are not case-sensitive.  Comments
take an entire line, and begin with a hash.

Most changes to this file will be to enable or disable individual sensors. It is
unlikely that many changes will need to be made once initial sensor details have
been entered (or if using existing sensor definitions).

Note that although each definition is referred to as a 'sensor', they actually
could more accurately be referred to as 'measurements'. For example, in the
standard setup there are two definitions relating to the DHT22 sensor, because
that particular physical sensor reads out both temperature and humidity.

There are a number of sections within the file - each one defines a single measurement.
The following fields are **mandatory** for every sensor (measurement) definition:
+ *filename* specifies the name of the Python script file for the sensor. No file
extension or path details are required. All analogue sensors use the same module;
this should be set to 'analogue' for all analogue sensors.
+ *enabled* specifies whether or not the sensor is enabled.
+ *sensorName* specifies the short name for the sensor. This must be unique to
this sensor. Do not include any spaces in this (use underscores if required). Note
that some sensor names are determined in the relevant Python module file (namely
measurements from the DHT22 and BMP085 sensors).
+ *description* is a longer (one-sentance) description of the sensor.

The following fields may be required for some sensor definitions, but not all:
+ *measurement* specifies the phenomenon which the sensor measures. Do not
include any spaces in this (use underscores if required).
+ *adcPin* specifies the ADC pin to which an analogue sensor is connected.
+ *pullDownResistance* specifies the value of the pull-down resistor used with the sensor.
+ *pullUpResistance* specifies the value of the pull-up resistor used with the sensor.
+ *pinNumber* specifies the GPIO pin which a sensor is connected to.
+ *sensorVoltage* specifies the voltage at which the sensor is running.
+ *i2cbus* specifies the port number for the i2c bus (0 for first version Raspberry Pi,
1 for subsequent revisions).
+ *mslp* specifies whether Mean Sea Level Pressure should be returned instead of
absolute local pressure (requires *altitude* to be set too).
+ *altitude* specifies the current altitude, for use with *mslp* in relation to
atmospheric pressure readings.


## Outputs
Output plugins are defined in the outputs.cfg file, which can be found in the cfg
directory. Values do not need any quote marks around them. Strings may include
spaces. There is equivalence between yes/on/true and between no/off/false; these
are not case-sensitive. Comments take an entire line, and begin with a hash.

Most changes to this file will be to enable or disable individual output plugins,
or change the location or format of their output.

There are a number of sections within the file - each one defines a single output
plugin. The following fields are **mandatory** for every output plugin definition:
+ *filename* specifies the name of the Python script file for the output plugin. No file
extension or path details are required.
+ *enabled* specifies whether or not the output plugin is enabled.
+ *calibration* specifies whether or not user-defined calibration functions should
be applied to raw data.
+ *description* is a longer (one-sentance) description of the sensor.

There are a number of other 




## Troubleshooting:
+ Ensure that airpictl.sh has been added to your $PATH environment variable.
+ Ensure that scripts are executable.