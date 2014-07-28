AirPi
========

A Raspberry Pi weather station and air quality monitor.

This is the code for the project located at http://airpi.es

Currently it is split into airpi.py, as well as multiple input and multiple output plugins. airpi.py collects data from each of the input plugins specified in sensors.cfg, and then passes the data provided by them to each output defined in outputs.cfg. The code for each sensor plugin is contained in the 'sensors' folder and the code for each output plugin in the 'outputs' folder.

Some of the files are based off code for the Raspberry Pi written by Adafruit: https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

For installation instructions, see airpi.es/kit.php

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

* Ability to start automatically at boot (does not require any user interaction).
  * This is set using the 'bootstart' parameter in 'settings.cfg'.
  * OutputDir parameter is now required, to avoid writing to /root when loading at boot.
* Renamed 'data' array to 'parameters' to better reflect its content, and avoid confusion with actual data.
* Added 'notifications' module which allow messages to be sent when errors occur. Includes email and tweet to start.
* Greater control of LED behaviour.
* Can disable error messages printed to screen.
* Can print to screen in CSV format.
* Added ability to record metadata to screen or CSV at start of a run, including Raspberry Pi serial no. and operator name.
* Standard print-to-screen format tidied up and made more digestable.
* Can automatically name CSV files and HTTP titles using date and hostname.
* Added ThingSpeak integration.
* Rounded Xively output to 2dp.
* Can kill the process a bit more nicely using Ctrl+C.
* Output modules requiring internet access will not be loaded if there is no connection available.
* Abort and inform user if no output modules are enabled.
* Code tidying:
  * Moved the check whether calibration is required into a super function called from each output subclass now.
  * Made multiple changes to all .py files in line with Pylint recommendations as per PEP 8 style guide.
  * Renamed 'data' to 'params' in output subclasses, to reflect their true nature and reduce confusion with data produced by sensors.
