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


def GetCurrentTemp():
    try:
      aList = ReadBoilerTemp.GetShowers()
      return [aList]
    except:
        print ("GetCurrentTemp Exception")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print (''.join('!! ' + line for line in lines) ) # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
        return [-1,1.0/120]

def SetRelay(PortNum,PostValue,offsetport=1):
      if PostValue ==0:
          controlrelay.SetRelayOff(PortNum)
          if offsetport > 0:
             controlrelay.SetRelayOff(PortNum+offsetport)
      else:
          controlrelay.SetRelayOn(PortNum) 
          if offsetport > 0:
             controlrelay.SetRelayOn(PortNum+offsetport)   

print ("Current temp is: ")
print (GetCurrentTemp())
status = controlrelay.ReadRelay(0)
if status == 0:
    print('Relay is off\n')
else:
    print('Relay is on\n')
if len(sys.argv) > 1:
    if sys.argv[1] == 'on':
        SetRelay(0,1)
    elif sys.argv[1] == 'On':
        SetRelay(0,1)
    elif sys.argv[1] == 'ON':
        SetRelay(0,1)
    elif sys.argv[1] == 'off':
        SetRelay(0,0)
    elif sys.argv[1] == 'Off':
        SetRelay(0,0)
    elif sys.argv[1] == 'OFF':
        SetRelay(0,0)

