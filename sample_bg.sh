#! /bin/bash

# Start AirPi sampling, as a background process.
# It's really just a wrapper to make life easier for non-Linux people.
# Haydn Williams 2014

thedir="/home/pi/AirPi"

thedate=`date +"%Y%m%d-%H%M"`
thehost=`hostname`
OUTPUT=$thehost-$thedate.log

echo "==========================================="
echo "Starting BACKGROUND AirPi sampling."
echo "Saving screen output to $thedir/$OUTPUT."
echo "Run 'airpistop.sh' to stop."
echo "==========================================="

nohup sudo python $thedir/airpi.py > $thedir/$OUTPUT &
