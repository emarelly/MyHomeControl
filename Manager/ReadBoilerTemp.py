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
# Val 4 % of boiler max heat
# Val 5 number of showers
# Val 5 Time.
def calcShowers(templist):
      TargetTemp = 39.0
      BoilerCapacuty = 200
      ShowerSize = 40.0
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
          TempList = [templist[1],templist[0],templist[2],int(Pr*100),int(Showers*100)/100.0,datetime.datetime.now()]
      output = open(pklFileName, 'wb')
      pickle.dump(TempList, output)
      output.close()
      return [(int(Showers*100)/100.0)*10,int(Pr*100)]
def GetShowers():
     
     try:
          print ("GetShowers")
          # return value [sensor 1, sensor2, sensor 3, % of max,NOF showers,time]
          if os.path.isfile(pklFileName):
            # Step 1 readt pkl file time to make sure it is current
            lastmodtime  = os.stat(pklFileName).st_mtime
             # File Modification time in seconds since epoch
            file_mod_time = round(os.stat(pklFileName).st_mtime)
            # Time in seconds since epoch for time, in which logfile can be unmodified.
            t = datetime.datetime.today() - datetime.timedelta(minutes=30)
            should_time = round(time.mktime(t.timetuple()))
            # Time in minutes since last modification of file
            last_time = round((int(time.time()) - file_mod_time) / 60, 2)
            if (file_mod_time - should_time) < 20:
              print ("CRITICAL:", pklFileName, "last modified", last_time, "minutes. Threshold set to 20 minutes")
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
        if sensors == None:
            for line in y['Temp Sensors']:
                resaults.append(line['Address'] + ' , ' + str( line['Temperature']))
        else:
            for sensor in sensors:
                for line in y['Temp Sensors']:
                    if line['Address'].find(sensor) >= 0:
                        resaults.append(float(line['Temperature']))
                        break
        #print (resaults)
        return(resaults)
    except:
        return ([])
class Temp(object):
 # mFrame = 0
  mQuit = 1
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
     else:
        self.ReadTempFrom1Wire
  def ReadTempFromESP(self,mintemp,targettemp,BoilerStatus):
  # Open the file that we viewed earlier so that python can see what is in it. Replace the serial number as before. 
    if len(self.filename) > 0 :
      f = open(self.filename,'a')
    #while (self.mQuit == 1):
    try:
            if len(self.filename) > 0 :
               fcur =open(self.filename+".current",'w')
            list=GetSensorsFromESP(self.url,['43692b06','45052b06','2f832a06']) 
            if len(list) == 0 and self.resetcount < 3:
               resetESP(ESP_RESET_PORT,10)
               self.resetcount = self.resetcount + 1
               f.write("ESP was reset...")
               f.flush()
               list=GetSensorsFromESP(self.url,['43692b06','45052b06','2f832a06']) 
            calc = calcShowers(list)
            target = [float(mintemp),float(targettemp),int(BoilerStatus)]
            if len(self.filename) > 0 :
               self.resetcount = 0
               f.write("{\"date\":\"" + time.strftime("%Y/%m/%d : %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + ',\"target\":' + str(target)+ '};\r\n')
               f.flush()
               fcur.write("{\"Date\":\"" + time.strftime("%Y/%m/%d %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + '\"}')
               fcur.close()
               
            print (time.strftime("%Y/%m/%d : %H:%M:%S" ) + " ->" + str(list) + '-> ' + str(calc))
            f.close()
            #time.sleep(self.interval)
    except:
            print (time.strftime("%Y/%m/%d : %H:%M:%S  " ) , sys.exc_info()[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print (''.join('!! ' + line for line in lines) ) # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
            if len(self.filename) > 0 :
                f.write(time.strftime("%Y/%m/%d : %H:%M:%S  " ) + str( sys.exc_info()[0])+ '\n')
                fcur.close()
                fcur =open(self.filename+".current",'w')
                fcur.write("{\"Date\":\"" + time.strftime("%Y/%m/%d %H:%M:%S" ) + '"\",\"System down\"}')
                fcur.close()
            f.close()
        #time.sleep(self.interval)
            
            
    if len(self.filename) > 0 : 
      f.close()
      fcur.close()

def ReadTempFrom1Wire(self,):
  # Open the file that we viewed earlier so that python can see what is in it. Replace the serial number as before. 
    try:
          Sensorlist = glob.glob('/mnt/1wire/28*')
          NOFSensors = len(Sensorlist)
          if NOFSensors == 0:
             Sensorlist = glob.glob('/mnt/1wire/28*')
             NOFSensors = len(Sensorlist)
    except:
           Sensorlist = glob.glob('/mnt/1wire/28*')
           NOFSensors = len(Sensorlist)
    if len(self.filename) > 0 :
      f = open(self.filename,'w')
      fcur =open(self.filename+".current",'w')
      # f.write(time.strftime("%Y/%m/%d : %H:%M:%S" ) + " ->" + str(Sensorlist) + '-> #,% \n')
      bSensorlist = []
      for i in range(len(Sensorlist)):
        # 45052B06 =#2  28.2F832A06 =3 28.43692B06=#1
          if '28.45052B06' in Sensorlist[i] or '28.43692B06' in Sensorlist[i] or '28.2F832A06' in Sensorlist[i]:  
              print (Sensorlist[i] + ' is part of the boiler sensors')
              bSensorlist.append(Sensorlist[i])
          else:
              print (Sensorlist[i] + ' is not part of the boiler sensors skiping ...')

      print (bSensorlist)
    i=11    
    while (self.mQuit == 1):
        try:
            if len(self.filename) > 0 :
               fcur =open(self.filename+".current",'w')
            list=[] 
            for x, device in enumerate(bSensorlist):
                tfile = open(device + "/temperature",'r')
                text = tfile.read() 
                tfile.close() 
                 # The first two characters are "t=", so get rid of those and convert the temperature from a string to a number. 
                temperature = float(text) * 1000
                # Put the decimal point in the right place and display it. 
                temperature = float(int(temperature/100)) / 10
                list.append(temperature)
                #print time.strftime("%Y/%m/%d : %H:%M:%S" ) + " -> " + str(temperature) + "C"
            if bSensorlist.count < 3 :
                list.append(-1)
                list.append(-1)
                list.append(-1)
            calc = calcShowers(list)

        
            if len(self.filename) > 0 :
               if i > 10 : 
                  f.write("{\"date\":\"" + time.strftime("%Y/%m/%d : %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + '};\r\n')
                  f.flush()
                  i=0
               #PRING CURRENT TEMP TO FILE
               BoilerStatus = controlrelay.ReadRelay(0)
               #print "BoilerStatus =" + str(BoilerStatus);
               fcur.write("{\"Date\":\"" + time.strftime("%Y/%m/%d %H:%M:%S" ) + "\",\"Temp\":" + str(list) + ',\"Capacity\":' + str(calc) + ',\"BoilerRelay\":\"' + str(BoilerStatus) + '\"}')
               fcur.close()
               i=i+1
            print (time.strftime("%Y/%m/%d : %H:%M:%S" ) + " ->" + str(list) + '-> ' + str(calc))
            time.sleep(self.interval)
        except:
            print (time.strftime("%Y/%m/%d : %H:%M:%S  " ) , sys.exc_info()[0])
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print (''.join('!! ' + line for line in lines))  # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
            if len(self.filename) > 0 :
                f.write(time.strftime("%Y/%m/%d : %H:%M:%S  " ) + str( sys.exc_info()[0])+ '\n')
                fcur.close()
                fcur =open(self.filename+".current",'w')
                fcur.write("{\"Date\":\"" + time.strftime("%Y/%m/%d %H:%M:%S" ) + '"\",\"System down\"}')
                fcur.close()
            f.flush()
        time.sleep(self.interval)
            
            
    if len(self.filename) > 0 : 
      f.close()
      fcur.close()

#MYTermo = Temp(60,'log.log','http://192.168.14.108')
#MYTermo.ReadTemp()
#print ("done ...")
