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
            if RelayMap.relaymap[RelayNum][2] == 'prop':
                ret = GetGPIOFromESP(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1])
            elif RelayMap.relaymap[RelayNum][2] == 'DingCgi':
                ret = GetGPIOFromDingtian(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1])
            else:
                print (" ReadRelay not found " + str(RelayNum))    
            print (" ReadRelay value " + str(ret))
            return(ret)
       except:
          print("ReadRelay Exception : " + traceback.format_exc())
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
          print("ReadRelay Exception : " + traceback.format_exc())
          return 0   
def SetRelayOn(RelayNum):
       try:
          #RelayNum = RelayNum -1
            if len(RelayMap.relaymap) > RelayNum and RelayNum >= 0:
                if RelayMap.relaymap[RelayNum][2] == 'prop':
                    ret = SetGPIOFromESP(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1],1)
                elif RelayMap.relaymap[RelayNum][2] == 'DingCgi':
                    ret = SetGPIOFromDingtian(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1],1)
                else:
                    print (" SetRelayOn not found " + str(RelayNum))
            print (" SetRelayOn value " + str(ret))
            return(ret)
       except:
          print("SetRelayOn Exception : " + traceback.format_exc())
          return    

def SetRelayOff(RelayNum):
      try:
          #RelayNum = RelayNum -1
            if len(RelayMap.relaymap) > RelayNum and RelayNum >= 0:
                if RelayMap.relaymap[RelayNum][2] == 'prop':
                    ret = SetGPIOFromESP(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1],0)
                elif RelayMap.relaymap[RelayNum][2] == 'DingCgi':
                    ret = SetGPIOFromDingtian(RelayMap.relaymap[RelayNum][0],RelayMap.relaymap[RelayNum][1],0)
                else:
                    print (" SetRelayOff not found " + str(RelayNum))
            print (" SetRelayOff value " + str(ret))
            return(ret)
      except:
          print("SetRelayOff Exception : " + traceback.format_exc())
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
          print("SetRelayOn Exception : " + traceback.format_exc())
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
          print("SetRelayOff Exception : " + traceback.format_exc())
          return    
def GetGPIOFromESP(url,GpioNumber):
    try:
        #print(url+ '/GetGPIO?id='+ str(GpioNumber))
        r = requests.get(url+ '/GetGPIO?id='+ str(GpioNumber), timeout=10)
        #j = '{ "Temp Sensors": [   {"Temperature": 24.31 ,"Address": "0x2815c22b0600003a"}]}'
        y =r.text.split('=')[1].strip()
        return(int(y))
    except:
        print("GetGPIOFromESP exception : " + traceback.format_exc())
        return ([])
def GetGPIOFromDingtian(url,GpioNumber):
    try:
       # print(url+ '/relay_cgi_load.cgi'+ str(GpioNumber))
        r = requests.get(url+ '/relay_cgi_load.cgi', timeout=10)
        y =r.text.split('&')
        if int(y[1]) == 0:
           if(int(y[2]) >= GpioNumber):
                print ('GetGPIOFromDingtian: values ' + r.text)
                return int(y[GpioNumber + 3])
           else:
                print ('GetGPIOFromDingtian: GPIO number to big' + str(GpioNumber))
                return ([])
        
        else:
          print ('GetGPIOFromDingtian: fail to read board')
          return []
        
    except:
        print("GetGPIOFromDingtian exception : " + traceback.format_exc())
        return ([])
def SetGPIOFromDingtian(url,GpioNumber,Value,password = 0):
    try:
        #print(url+ '/GetGPIO?id='+ str(GpioNumber))
        r = requests.get(url+ '/relay_cgi.cgi?type=0&relay=' + str(GpioNumber) +'&on=' +str(Value) +'&time=0&pwd='+ str(password) + '&', timeout=10)
        
        y =r.text.split('&')
        if int(y[1]) == 0:
           if(int(y[3]) == GpioNumber):
                print ('SetGPIOFromDingtian: values ' + r.text)
                return int(y[4])
           else:
                print ('SetGPIOFromDingtian: GPIO number mism for gpio ' + str(GpioNumber) + 'result received :' + r.text)
                return ([])
        
        else:
          print ('SetGPIOFromDingtian: fail to read board')
          return []
        
    except:
        print("SetGPIOFromDingtian exception : " + traceback.format_exc())
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
        print("SetGPIOFromESP exception : " + traceback.format_exc())
        return ([])


#SetRelayOn(1)
#ReadRelay(1)
#SetRelayOff(1)
#ReadRelay(1)
