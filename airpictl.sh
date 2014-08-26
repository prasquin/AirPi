#! /bin/bash

# Control AirPi sampling.
# It's really just a wrapper to make life easier for non-Linux people.
# Haydn Williams 2014

# Set variables
DIR=`pwd`
RUNDATE=`date +"%Y%m%d-%H%M"`
HOST=`hostname`
OUTPUT=$HOST-$RUNDATE.out

# Start fresh
clear;

# Check whether anything is already running
if `ps aux | grep -v "grep" | grep -q "sudo.*airpi.py"`; then
    case $1 in
        normal)
            ;&
        bg)
            ;&
        unatt)
            echo "[AirPi] Abort - it looks like the AirPi is already sampling."
            echo "[AirPi] You can use 'sudo ./airpictl stop' to stop it."
            exit 1
            ;;
    esac
fi

# Run in the appropriate mode
case $1 in 
    normal)
        echo "[AirPi] Starting normal AirPi sampling."
        echo "[AirPi] This run will end if you log out."
        echo "[AirPi] Press Ctrl +  C to stop."
        sudo python $DIR/airpi.py
        ;;
    bg)
        echo "[AirPi] Starting BACKGROUND AirPi sampling."
        echo "[AirPi] This run will end if you log out."
        echo "[AirPi] Saving screen output to $DIR/log/$OUTPUT."
        echo "[AirPi] To stop sampling, run: 'sudo ./airpictl.sh stop'"
        sudo python $DIR/airpi.py > $DIR/log/$OUTPUT &
        ;;
    unatt)
        echo "[AirPi] Starting UNATTENDED AirPi sampling."
        echo "[AirPi] This run will continue even if you log out."
        echo "[AirPi] Saving screen output to $DIR/log/$OUTPUT."
        echo "[AirPi] To stop sampling, run: 'sudo ./airpictl.sh stop'"
        nohup sudo python $DIR/airpi.py > $DIR/log/$OUTPUT &
        ;;
    stop)
        if `ps aux | grep -v "grep" | grep -q "sudo.*airpi.py"`; then
            echo "[AirPi] Stopping all AirPi sampling."
            echo "[AirPi] Use Ctrl+C to stop 'normal' runs."
            kill `ps aux | grep -v "grep" | grep "sudo.*airpi.py" | awk '{print $2}'`
        else
            echo "[AirPi] Could not find any running processes to stop."
        fi
        ;;
    status)
        if `ps aux | grep -v "grep" | grep -q "sudo.*airpi.py"`; then
            echo "[AirPi] Status: SAMPLING"
            echo "[AirPi] To stop, use 'sudo ./airpictl.sh stop'"
        else
            echo "[AirPi] Status: Not currently sampling."
        fi
        ;;
    *)
        echo "[AirPi] No sampling mode requested."
        echo "[AirPi] Please specify one of the following modes:"
        echo "[AirPi] airpictl.sh normal  <- Runs normally"
        echo "[AirPi] airpictl.sh bg      <- Background; stops when your login session ends."
        echo "[AirPi] airpictl.sh unatt   <- Unattended; continues even after you log out."
        echo "[AirPi] airpictl.sh status  <- Shows whether AirPi is currently sampling or not."
        echo "[AirPi] sudo ./airpictl.sh stop  <- Stops any existing run."
        ;;
esac
