#!/bin/bash 
cd /home/pi/Boiler/
#/usr/bin/python BoilerControl.py >BoilerControl.log &
rm -f BoilerManager.log.001 
mv -f BoilerManager.log BoilerManager.log.001 
/usr/bin/python3 -u BoilerManager.py >BoilerManager.log &
rm -f TimerManager.log.001 mv -f TimerManager.log TimerManager.log.001 
/usr/bin/python3 -u TimerManager.py >TimerManager.log &
