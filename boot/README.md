This directory is only concerned with the automatic recording of AirPi data when the Raspberry Pi boots.
This is useful if, for example, you are running the unit with a battery and no monitor / keyboard, as
the AirPi will start sampling as soon as the Raspberry pi starts up; you do not need to log in, enter
any text or confirm anything.

If you will only ever be manually starting and stopping sampling in the 'normal' fashion, you can ignore
this directory entirely.



Installation Instructions:
==========================
1) Copy the startup script to the /etc/init.d directory:
sudo cp /home/pi/AirPi/boot/airpibootstart /etc/init.d/airpibootstart
2) Register the startup script:
sudo update-rc.d airpibootstart defaults
3) Use the "bootstart" option in the "settings.cfg" file to decide when to automatically sample.

The 'airpistop.sh' script kills the AirPi python script; it does not shut it down gracefully or anything
nice like that! To run it without putting the full path in every time, you can add the folder to your
PATH by adding the following line to your ~/.profile or ~/.bashrc file:
export PATH=/home/pi/AirPi/boot:$PATH 

If you ever need to remove the startup service:
sudo update-rc.d -f airpibootstart remove
