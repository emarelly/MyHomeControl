#!/bin/bash
#This script run BoilerControler.py
cd /home/pi/BoilerControler/
sudo -u pi mv /home/pi/BoilerControler/BoilerControler.log /home/pi/BoilerControler/BoilerControler.001.log
sudo -u pi /usr/bin/python3 -u BoilerControler.py >> /home/pi/BoilerControler/BoilerControler.log &



