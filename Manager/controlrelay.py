import glob
import time
import sys
import traceback
import os
import requests
# map table url, GPIO #
import RelayMap
def ReadRelay(RelayNum):
       try:
          #RelayNum = RelayNum -1
          if len(RelayMap.relaymap) > RelayNum and RelayNum >= 0:
            print (" ReadRelay " + str(RelayNum))
            ret = GetGPIOFromESP(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1])
            print (" ReadRelay value " + str(ret))
            return(ret)
       except:
          print ("ReadRelay Exception")
          exc_type, exc_value, exc_traceback = sys.exc_info()
          lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
          print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
          return 0   
def ReadRelay1Wire(RelayNum):
       try:
           print (" ReadRelay " + str(RelayNum))
           devicelist = glob.glob('/mnt/1wire/29*/PIO.' + str(RelayNum))
           NOFSensors = len(devicelist)
           if NOFSensors == 1:
             tfile = open(devicelist[0],'r')
             text = tfile.readline() 
             tfile.close() 
             print (" ReadRelay value " + text)
             return(int(text))
       except:
          print ("ReadRelay Exception")
          exc_type, exc_value, exc_traceback = sys.exc_info()
          lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
          print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
          return 0   
def SetRelayOn(RelayNum):
       try:
          #RelayNum = RelayNum -1
          if len(RelayMap.relaymap) > RelayNum and RelayNum >= 0:
            print (" SetRelayOn " + str(RelayNum))
            ret = SetGPIOFromESP(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1],1)
            print (" SetRelayOn value " + str(ret))
            return(ret)
       except:
          print ("SetRelayOn Exception")
          exc_type, exc_value, exc_traceback = sys.exc_info()
          lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
          print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
          return    

def SetRelayOff(RelayNum):
      try:
          #RelayNum = RelayNum -1
          if len(RelayMap.relaymap) > RelayNum and RelayNum >= 0:
            print (" SetRelayOff " + str(RelayNum))
            ret = SetGPIOFromESP(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1],0)
            print (" SetRelayOff value " + str(ret))
            return(ret)
      except:
          print ("SetRelayOn Exception")
          exc_type, exc_value, exc_traceback = sys.exc_info()
          lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
          print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
          return    
def SetRelayOn1Wire(RelayNum):
      try:
           print (" SetRelayOn")
           devicelist = glob.glob('/mnt/1wire/29*/PIO.' + str(RelayNum))
           NOFSensors = len(devicelist)
           print ("device name is (on): " + devicelist[0] + " count = " + str(NOFSensors))
           if NOFSensors == 1:
             tfile = open(devicelist[0],'w')
             text = tfile.write("1") 
             tfile.close()
      except:
          print ("SetRelayOn Exception")
          exc_type, exc_value, exc_traceback = sys.exc_info()
          lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
          print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
          return    
def SetRelayOff1Wire(RelayNum):
      try:
           print ("SetRelayOff")
           devicelist = glob.glob('/mnt/1wire/29*/PIO.' + str(RelayNum))
           NOFSensors = len(devicelist)
           print ("device name is(off): " + devicelist[0] + "count = " + str(NOFSensors))
           if NOFSensors == 1:
             tfile = open(devicelist[0],'w')
             text = tfile.write("0") 
             tfile.close() 
      except:
          print ("SetRelayOff Exception")
          exc_type, exc_value, exc_traceback = sys.exc_info()
          lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
          print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
          return    
def GetGPIOFromESP(url,GpioNumber):
    try:
        #print(url+ '/GetGPIO?id='+ str(GpioNumber))
        r = requests.get(url+ '/GetGPIO?id='+ str(GpioNumber), timeout=10)
        #j = '{ "Temp Sensors": [   {"Temperature": 24.31 ,"Address": "0x2815c22b0600003a"}]}'
        y =r.text.split('=')[1].strip()
        return(int(y))
    except:
        return ([])
def SetGPIOFromESP(url,GpioNumber,Value):
    try:
        if Value > 0:
            Value = 1
        else:
            Value = 0
        r = requests.get(url+ '/SetGPIO?id='+ str(GpioNumber)+';value='+str(Value), timeout=10)
        #j = '{ "Temp Sensors": [   {"Temperature": 24.31 ,"Address": "0x2815c22b0600003a"}]}'
        r = requests.get(url+ '/GetGPIO?id='+ str(GpioNumber), timeout=10)
        y =r.text.split('=')[1].strip()
        return(int(y))
    except:
        return ([])


#SetRelayOn(1)
#ReadRelay(1)
#SetRelayOff(1)
#ReadRelay(1)
