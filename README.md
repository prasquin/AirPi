AirPi
========

A Raspberry Pi weather station and air quality monitor.

This is the code for the project located at http://airpi.es

Currently it is split into airpi.py, as well as multiple input and multiple output plugins. airpi.py collects data from each of the input plugins specified in sensors.cfg, and then passes the data provided by them to each output defined in outputs.cfg. The code for each sensor plugin is contained in the 'sensors' folder and the code for each output plugin in the 'outputs' folder.

Some of the files are based off code for the Raspberry Pi written by Adafruit: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

For installation instructions, see airpi.es/kit.php

For ease of use when working with scripts, you may want to add the AirPi folder to your $PATH.

Changes - Fred Sonnenwald
-------------------------
This development branch of the AirPi code adds several features and bugfixes that I've developed as part of my http://pi.gate.ac.uk/ AirPi project.

It additionally incorporates changes by Jon Hogg (jncl), which include code cleanups, error logging, and GPS sensor support.

New features:
* Support for UVI-01 sensor
* Can disable LEDs
* Raingauge support
* Support for TGS-2600 Air Quality sensor
* CSV logging
* Built in HTTP server to display results nicely
  * Looks pretty using Twitter Bootstrap (http://getbootstrap.com/)
  * RSS feed
  * Nice graphs using Flot (http://www.flotcharts.org/)
  * Can load in CSV history for long period graphs
  * HTTP/1.0 or HTTP/1.1
* Sensor calibration, not just raw values
* GPS sensor support (untested by me, so may not be compatible with the HTTP or CSV code)

Bugfixes:
* Pressure sensor calibration (jaceydowell)
* Could not change mslp setting in pressure sensor
* Don't just ignore failed readings (record 0 instead)
* High CPU usage
* Hopefully fixed an issue with readings hanging on DHT22


Changes - Haydn Williams
------------------------
It additionally incorporates changes by Haydn Williams (github.com/haydnw), which include the following:

* Added 'airpictl.sh' script to control sampling in different modes.
  * Run './airpictl.sh' to see options and usage.
  * Includes 'background' and 'unattanded', so you can SSH into your Pi, start it, then quit.
* Added ability to output average data (e.g. read every 1 min for 10 mins, then output the average for the 10 mins).
  * Controlled by "averageFreq" parameter in 'cfg/settings.cfg' - set to at least twice sampleFreq to enable averaging.
* Added ability to do 'dummy runs' for a predefined period before a run starts properly, to ensure all sensors are
  up and running, and won't just report back zeroes.
  * Controlled by "dummyduration" parameter in 'cfg/settings.cfg' - set to 0 for no dummy runs. Recommended is 15.
* Added ability to stop a run after X samples.
  * Controlled by "stopafter" parameter in 'cfg/settings.cfg' - set to 0 to run indefinitely.
* Added ability to record metadata such as Raspberry Pi serial no. and operator name at start of run.
  * Controlled by "metadatareqd" parameters in 'cfg/outputs.cfg' - set to True to output metadata.
* Added ability to start automatically at boot for headless operation (does not require any user interaction).
  * Controlled by 'bootstart' parameter in 'cfg/settings.cfg'.
  * See the 'boot' directory for more info.
* Added 'Notifications' module which allow messages to be sent when errors occur. Includes email, SMS and tweet.
  * Controlled by 'cfgs/notifications.cfg'.
* Added warning if GPS socket not detected when GPS sensor enabled.
* Added the following new options to 'cfg/settings.cfg':
  * Greater control of LED behaviour.
  * Can disable error messages printed to screen.
  * Can print to screen in CSV format.
* Standard print-to-screen format tidied up and made more digestable.
* Can automatically name CSV files and HTTP titles using date and hostname.
  * Controlled by use of '<date>' and '<hostname>' in 'cfg/outputs.cfg'
* Added JSON output.
* Added ThingSpeak output.
* Added dweet output.
* Rounded Xively output to 2dp.
* Can kill the process a bit more nicely using Ctrl+C.
* 'outputDir' parameter is now required for csvoutput, to avoid writing to /root when loading at boot.
  * Needs to be in [CSVOutput] section of 'cfg/outputs.cfg'.
* Moved all config files to 'cfg' directory.
* Moved all log files (and redirected output from airpictl.sh) to 'log' directory.
* Output modules requiring internet access will not be loaded if there is no connection available.
* Abort and inform user if no output modules are enabled.
* Renamed 'data' array to 'parameters' to better reflect its content, and avoid confusion with actual data.
* Started porting to Python 3 in 'python3' branch (work in progress; no feature parity between versions at present).
* Code tidying:
  * Moved the check whether calibration is required into a super function called from each output subclass now.
  * Made multiple changes to all .py files in line with Pylint recommendations as per PEP 8 style guide.
  * Renamed 'data' to 'params' in output subclasses, to reflect their true nature and reduce confusion with data produced by sensors.
  * Massive refactoring of airpi.py by extracting methods to facilitate code reuse and simplificaiton.
