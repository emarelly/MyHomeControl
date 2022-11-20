#!/bin/bash
#This script run BoilerControler.py
cd /home/pi/BoilerControler/
mv /home/pi/BoilerControler/BoilerControler.log /home/pi/BoilerControler/BoilerControler.001.log
sudo /usr/bin/python BoilerControler.py >> /home/pi/BoilerControler/BoilerControler.log &



