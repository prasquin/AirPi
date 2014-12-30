\# ==========================================================================  
\# File:     installation.md  
\# Purpose:  Instructions for installing software to support an AirPi.  
\# Author:   Haydn Williams <pi@hwmail.co.uk>  
\# Date:     October 2014  
\# ==========================================================================  

# AirPi Software Installation Instructions

This document assumes the following:
+ You have a functioning Raspberry Pi running the
[December 2014 release of Raspbian Wheezy](http://downloads.raspberrypi.org/raspbian_latest).
+ The Raspberry Pi can connect to the internet.
+ You are comfortable editing text files in a program of your
choice (*e.g.* *[vi](http://ex-vi.sourceforge.net)* or [Nano](http://www.nano-editor.org)).
+ You have correctly assembled your AirPi, and connected it to the GPIO
header on the Raspberry Pi.

1.  Ensure the system is up-to-date:
	```shell
	sudo apt-get update
	sudo apt-get upgrade
	```

1.  Install required support packages:
	```shell
	sudo apt-get install python-dev python-smbus python-setuptools python-requests python3-dev python3-requests libxml2-dev libxslt1-dev python-lxml i2c-tools
	```

1.  [OPTIONAL] Install Twitter support (for Notifications):
	```shell
	easy_install Twitter
	```

1.  Enable Raspberry Pi [I2C](https://learn.sparkfun.com/tutorials/i2c) support (for BMP085 sensor):
	```shell
	sudo sed -i 's/#i2c-bcm2708/i2c-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
	sudo echo "i2c-dev" >> /etc/modules
	```

1.  Reboot and check the AirPi hardware is recognised:
	```shell
	sudo reboot
	sudo i2cdetect -y 1
	```
	Successful output looks like this:
	```shell
     	0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
	00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
	10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
	20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
	30: -- -- -- -- -- -- -- -- -- -- -- UU -- -- -- -- 
	40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
	50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
	60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
	70: -- -- -- -- -- -- -- 77
	```
	*N.B. If you have an original Raspberry Pi (Model B first revision) then you'll
	need to use a zero at the end of the command above, because the I2C port was
	[changed between revisions](http://www.raspberrypi.org/upcoming-board-revision/).
	This means you will also have to change the `i2cbus` options in the
	`cfg/sensors.cfg` sensor definitions file (see docs/usage.md for details).*

1.  [OPTIONAL] Enable GPS, then check it works:
	```shell
	sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
	cgps -s
	```

1.  Download the [AirPi software](https://github.com/haydnw/airpi):
	```shell
	cd ~
	git clone https://github.com/haydnw/airpi AirPi
	sudo echo "export PATH=$PATH:/home/pi/AirPi" >> /home/pi/.profile
	```

For information about how to use the software once installed, see the file
`usage.md` in the `docs` directory.