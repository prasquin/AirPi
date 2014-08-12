#! /bin/bash

# Control AirPi sampling.
# It's really just a wrapper to make life easier for non-Linux people.
# Haydn Williams 2014

# Set variables
DIR=`pwd`
RUNDATE=`date +"%Y%m%d-%H%M"`
HOST=`hostname`
OUTPUT=$HOST-$RUNDATE.out

# Check whether anything is already running
if `ps aux | grep -v "grep" | grep -q "sudo.*airpi.py"`; then
    if [ "$1" != "stop" ]; then
        echo "[AirPi] Abort - it looks like the AirPi is already sampling."
        echo "[AirPi] You can use 'sudo ./airpictl stop' to stop it."
        exit 1
    fi
fi

# Run in the appropriate mode
if [ "$1" == "normal" ]
then
    echo "[AirPi] Starting normal AirPi sampling."
    echo "[AirPi] This run will end if you log out."
    echo "[AirPi] Press Ctrl +  C to stop."
    sudo python $DIR/airpi.py
elif [ "$1" == "bg" ]
then
    echo "[AirPi] Starting BACKGROUND AirPi sampling."
    echo "[AirPi] This run will end if you log out."
    echo "[AirPi] Saving screen output to $DIR/log/$OUTPUT."
    echo "[AirPi] To stop sampling, run: 'sudo ./airpictl.sh stop'"
    
    sudo python $DIR/airpi.py > $DIR/log/$OUTPUT &

elif [ "$1" == "unatt" ]
then

    echo "[AirPi] Starting UNATTENDED AirPi sampling."
    echo "[AirPi] This run will continue even if you log out."
    echo "[AirPi] Saving screen output to $DIR/log/$OUTPUT."
    echo "[AirPi] To stop sampling, run: 'sudo ./airpictl.sh stop'"

    nohup sudo python $DIR/airpi.py > $DIR/log/$OUTPUT &

elif [ "$1" == "stop" ]
then

    if `ps aux | grep -v "grep" | grep -q "sudo.*airpi.py"`; then
        echo "[AirPi] Stopping all AirPi sampling."
        echo "[AirPi] Use Ctrl+C to stop 'normal' runs."
        kill `ps aux | grep -v "grep" | grep "sudo.*airpi.py" | awk '{print $2}'`
    else
        echo "[AirPi] Could not find any running processes to stop."
    fi

else

    echo "[AirPi] No sampling mode requested."
    echo "[AirPi] Please specify one of the following modes:"
    echo "[AirPi] airpictl.sh normal  <- Runs normally"
    echo "[AirPi] airpictl.sh bg      <- Background; stops when your login session ends."
    echo "[AirPi] airpictl.sh unatt   <- Unattended; continues even after you log out."
    echo "[AirPi] sudo ./airpictl.sh stop  <- Stops any existing run."

fi
