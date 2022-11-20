#import Tkinter
import glob
import time
import array
import datetime 
import os.path
import pickle
import ReadBoilerTemp
import controlrelay
import json
import traceback
import sys

def SetRelay(PortNum,PostValue,offsetport=0):
      if PostValue ==0:
          controlrelay.SetRelayOff(PortNum)
          if offsetport > 0:
             controlrelay.SetRelayOff(PortNum+offsetport)
      else:
          controlrelay.SetRelayOn(PortNum) 
          if offsetport > 0:
             controlrelay.SetRelayOn(PortNum+offsetport)   

if len(sys.argv) == 2:
	status = controlrelay.ReadRelay(int(sys.argv[1]))
	if status == 0:
		print('Relay is off\n')
	else:
		print('Relay is on\n')
elif len(sys.argv) > 2:
    status = controlrelay.ReadRelay(int(sys.argv[1]))
    print('val= ' + str(status))
    if status == 0:
		print('Relay #' + sys.argv[1] + ' is off\n')
    else:
		print('Relay #' + sys.argv[1] + ' is on\n')
    if sys.argv[2].lower() == "on" :
        SetRelay(int(sys.argv[1]),1)
    elif sys.argv[2].lower() == 'off':
        SetRelay(int(sys.argv[1]),0)
    status = controlrelay.ReadRelay(int(sys.argv[1]))
    print('status = ' +str(status))
    if status == 0:
		print('Relay #' + sys.argv[1] + ' is off\n')
    else:
		print('Relay #' + sys.argv[1] + ' is on\n')
    
    


