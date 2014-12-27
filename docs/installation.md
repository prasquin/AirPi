\# ============================================================================
\# File:     installation.md
\# Purpose:  Instructions for installing software to support an AirPi.
\# Author:   Haydn Williams <pi@hwmail.co.uk>
\# Date:     October 2014
\# ============================================================================

# AirPi Software Installation Instructions

1. Ensure system is up-to-date:
```shell
sudo apt-get update
sudo apt-get upgrade
```

1. Install required support packages:
```shell
sudo apt-get install python-dev python-smbus python-setuptools python-requests python3-dev python3-requests libxml2-dev libxslt1-dev python-lxml i2c-tools
```

1. [OPTIONAL] Install Twitter support:
```shell
easy_install Twitter
```

1. Enable Raspberry Pi I2C support:
```shell
sudo sed -i 's/#i2c-bcm2708/i2c-bcm2708/g' /etc/modprobe.d/raspi-blacklist.conf
sudo echo "i2c-dev" >> /etc/modules
```

1. Reboot and check the AirPi hardware is recognised:
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
This means you will also have to change the 'i2cbus' options in the
cfg/sensors.cfg sensor definitions file (see docs/usage.md for details).*

1. [OPTIONAL] Enable GPS, then check it works:
```shell
sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
cgps -s
```

1. Download the [AirPi software](https://github.com/haydnw/airpi):
```shell
cd ~
git clone https://github.com/haydnw/airpi AirPi
sudo echo "export PATH=$PATH:/home/pi/AirPi" >> /home/pi/.profile
```