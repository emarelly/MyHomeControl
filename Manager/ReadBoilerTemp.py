#import Tkinter
import glob
import time
import pickle
#import graph
import os
import datetime
import sys
import controlrelay
import traceback # DEBUG
import requests
import json
import RPi.GPIO as GPIO
pklFileName  = 'BoilerTemp.pkl'
ESP_RESET_PORT = 27
## esp RESET VIA REALY THAT SEND RESET COMMAND
def resetESP(port,reboottimeinsec):
    relay = port
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay, GPIO.OUT)
    GPIO.output(relay, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(relay, GPIO.LOW)
    time.sleep(reboottimeinsec)
def clearport(port):
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(port, GPIO.OUT)
  GPIO.output(port, GPIO.LOW)
   
#temp structure defenition
# list of 6 values
# Val 1 Sensor 1
# Val 2 Sensor 2
# Val 3 Sensor 3 
# Val 4 number of showers new cals
# Val 5 number of showers
# Val 5 Time.
def calcShowers(templist):
      TargetTemp = 39.0
      BoilerCapacuty = 200
      ShowerSize = 40.0
      numberofsensors = 3
      ShowersINBoiler = BoilerCapacuty/ ShowerSize
      if len(templist) < 3 or templist[0] == -1 or templist[1] == -1 or templist[2] == -1:  
          Av = -1.0
          Pr = -1.0
          Showers = -1.0
          TempList = [-1,-1,-1,int(Pr*100),int(Showers*100)/100.0,datetime.datetime.now()]
      else: 
          Av = float(templist[0] + templist[1] + templist[2])/3.0
          Pr = float(Av)/TargetTemp - 0.6
          Showers =  Pr * ShowersINBoiler # P1 + P2 + P3
          th = float(templist[2]/TargetTemp)
          tm = 0
          if th >=1:
            tm = float(templist[1]/TargetTemp)
            if tm < 1:
              tm = tm*numberofsensors/ShowersINBoiler
          tl = 0
          if tm >=1:
            tl = float(templist[0]/TargetTemp)
            if tl < 1:
              tl = tl*numberofsensors/ShowersINBoiler
          Showersnew = th+tm+tl
          
          if Showersnew >=1:
            Showersnew = Showersnew * ShowersINBoiler/numberofsensors
            
          TempList = [templist[1],templist[0],templist[2],int(Showersnew*100)/100.0,int(Showers*100)/100.0,datetime.datetime.now()]
      output = open(pklFileName, 'wb')
      pickle.dump(TempList, output)
      output.close()
      return [(int(Showers*100)/100.0)*10,(int(Showersnew*100)/100.0)*10]
def GetShowers():
     
     try:
          print ("GetShowers")
          # return value [sensor 1, sensor2, sensor 3, % of max,NOF showers,time]
          if os.path.isfile(pklFileName):
            file_mod_time = round(os.stat(pklFileName).st_mtime)
            last_time = round((int(time.time()) - file_mod_time) / 60, 2)
            if last_time > 20:
              print ("CRITICAL:", pklFileName, "last modified", last_time, "minutes ago. (Threshold set to 20 minutes)")
              return [-1,-1,-1,-3,-1,datetime.datetime.now()]
            else:
              print ("OK. Command completed successfully for ", pklFileName, " ", last_time, "minutes ago.")
            #Step 2: read pkl file and return List
            pkl_file = open(pklFileName, 'rb')
            alist = pickle.load(pkl_file)
            pkl_file.close()
            return alist
          else:
           return [-1,-1,-1,-1,-1,datetime.datetime.now()]
           #return [20,20,20,4,6,datetime.datetime.now()] # Debug
     except:
           print ("CRITICAL:", pklFileName, "not found")
           return [-1,-1,-1,-1,-1,datetime.datetime.now()]
           #return [20,20,20,4,6,datetime.datetime.now()] # Debug
def GetSensorsFromESP(url,sensors):
    try:
        clearport(ESP_RESET_PORT)
        r = requests.get(url+ '/temp', timeout=5)
        #j = '{ "Temp Sensors": [   {"Temperature": 24.31 ,"Address": "0x2815c22b0600003a"}]}'
        y = json.loads(r.text.replace('}  {','} , {'))
        resaults =[]
        othersensors = []
        if sensors == None:
            for line in y['Temp Sensors']:
                resaults.append(line['Address'] + ' , ' + str( line['Temperature']))
        else:
            othersensor = ''
            for sensor in sensors:
                for line in y['Temp Sensors']:
                    othersensor = line
                    if line['Address'].find(sensor) >= 0:
                        resaults.append(float(line['Temperature']))
                        othersensor = ''
                        break
            if len(othersensor) > 0:
              othersensors.append(float(othersensor['Temperature']))
        #print (resaults)
        return([resaults,othersensor])
    except:
        return ([],[])
class Temp(object):
  interval = 10
  filename= ""
  url=""
  resetcount = 0
  def __init__(self, *args, **kwargs):
     self.interval = args[0]
     self.filename =args[1]
     if len(args) > 2:
       self.url = args[2]
  def ReadTemp(self,mintemp,targettemp,BoilerStatus):
     if len(self.url) > 0:
        self.ReadTempFromESP(mintemp,targettemp,BoilerStatus)

  def ReadTempFromESP(self,mintemp,targettemp,BoilerStatus):
    if len(self.filename) > 0 :
      f = open(self.filename,'a')
    try:
            if len(self.filename) > 0 :
               fcur =open(self.filename+".current",'w')
            if len(self.filename) > 0 :
               fother =open('other'+self.filename,'w')
            lists=GetSensorsFromESP(self.url,['43692b06','45052b06','2f832a06']) 
            list = lists[0]
            if len(list) == 0 and self.resetcount < 3:
               resetESP(ESP_RESET_PORT,10)
               self.resetcount = self.resetcount + 1
               f.write("ESP was reset...\r\n")
               f.flush()
               lists=GetSensorsFromESP(self.url,['43692b06','45052b06','2f832a06']) 
               list = lists[0]
            calc = calcShowers(list)
            target = [float(mintemp),float(targettemp),int(BoilerStatus)]
            if len(self.filename) > 0 :
               self.resetcount = 0
               f.write("{\"date\":\"" + time.strftime("%Y/%m/%d : %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + ',\"target\":' + str(target)+ '};\r\n')
               f.flush()
               fother.write("{\"date\":\"" + time.strftime("%Y/%m/%d : %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + ',\"target\":' + str(target) + ",\"other\":" + str(lists[1])+ '};\r\n')
               fother.flush()
               fcur.write("{\"Date\":\"" + time.strftime("%Y/%m/%d %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + '\"}')
               fcur.close()
               f.close()
               fother.close()
            print (time.strftime("%Y/%m/%d : %H:%M:%S" ) + " ->" + str(list) + '-> ' + str(calc))
            
    except:
            print (time.strftime("%Y/%m/%d : %H:%M:%S  " ) , sys.exc_info()[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print (''.join('!! ' + line for line in lines) ) # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
            if len(self.filename) > 0 :
                f.write(time.strftime("%Y/%m/%d : %H:%M:%S  " ) + str( sys.exc_info()[0])+ '\r\n')
                fcur.close()
                fcur =open(self.filename+".current",'w')
                fcur.write("{\"Date\":\"" + time.strftime("%Y/%m/%d %H:%M:%S" ) + '"\",\"System down\"}')
                fcur.close()
            f.close()
              
            
    if len(self.filename) > 0 : 
      f.close()
      fcur.close()

#MYTermo = Temp(60,'log.log','http://192.168.14.108')
#MYTermo.ReadTemp()
#print ("done ...")
