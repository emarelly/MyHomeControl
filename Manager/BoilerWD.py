import time
import os
import glob
import time
import signal
#import Temp
import tkinter

import ReadBoilerTemp
import datetime

import controlrelay
import subprocess
import traceback # DEBUG
import datetime
import sys

pklFileName  = 'BoilerTemp.pkl'
GPIO_ERROR = "GPIO Error"
OK = "OK"
APP_ERROR = "App error"

TEMP_FLAG = 1
GUI_FLAG = 10
CONTROL_FLAG = 100
MANAGER_FLAG = 1000
TIMER_FLAG = 10000
def VerifyTempSensor():
    aList = ReadBoilerTemp.GetShowers()
#    print "ReadBoile return " + str(aList)
    if (aList[4] < 0) :
      print ("Can't read temp checking Sensors...")
      try:
          Sensorlist = glob.glob('/mnt/1wire/28*')
          NOFSensors = len(Sensorlist)
          if NOFSensors == 0:
             Sensorlist = glob.glob('/mnt/1wire/28*')
             NOFSensors = len(Sensorlist)
      except:
           NOFSensors = 0
      if (NOFSensors == 0 ) :
          return GPIO_ERROR
      else:
          return APP_ERROR

    else:
      return OK
def VerifyManagerStatus():
	aList = ReadBoilerTemp.GetShowers()
	if aList[3] == -3:
	    return False
	else:
		return True
            
def proct(pid):
    try:
        with open(os.path.join('/proc/', pid, 'stat'), 'r') as pidfile:
            proctimes = pidfile.readline()
            # get utime from /proc/<pid>/stat, 14 item
            utime = proctimes.split(' ')[13]
            # get stime from proc/<pid>/stat, 15 item
            stime = proctimes.split(' ')[14]
            # count total process used time
            proctotal = int(utime) + int(stime)
            return(float(proctotal))
    except IOError as e:
        print('ERROR: %s' % e)
        return -1


def cput():
    try:
        with open('/proc/stat', 'r') as procfile:
            cputimes = procfile.readline()
            cputotal = 0
            # count from /proc/stat: user, nice, system, idle, iowait, irc, sof$
            for i in cputimes.split(' ')[2:]:
                i = int(i)
                cputotal = (cputotal + i)
            return(float(cputotal))
    except IOError as e:
        print('ERROR: %s' % e)
        return -1
def GetProcessCPU(pid):

  try:
    proctotal = proct(pid)
    cputotal = cput()
    pr_proctotal = proctotal
    pr_cputotal = cputotal
    time.sleep(1)
    proctotal = proct(pid)
    cputotal = cput()
    res = ((proctotal - pr_proctotal) / (cputotal - pr_cputotal) * 100)
    print('CPu Usage: %s\n' % round(res, 1))
    return  round(res, 1)
  except:
    return -1


def CheckProcess():
  pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
  count = 0
  temp = 0
  gui = 0
  control = 0
  Manager = 0
  Timer = 0
  for pid in pids:
    try:
        file = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        #print file
        if(file.count("readtemp.py") > 0):
          count=count+TEMP_FLAG
          temp=pid
          #print "1st found"
        if(file.count("GuiTest.py") > 0):
          count=count+GUI_FLAG
          gui=pid
          #print "Sec found"
        if(file.count("BoilerControl.py")> 0):
          count=count+CONTROL_FLAG
          control = pid
          #print "3rd found"
        if(file.count("BoilerManager.py")> 0):
	        if VerifyManagerStatus() == True:
	              count=count+MANAGER_FLAG
	        Manager = pid
          #print "4rd found"  
        if(file.count("TimerManager.py")> 0):
          count=count+TIMER_FLAG
          Timer = pid
          #print "5rd found"  
    except:
        print ("")
  return [count,temp,gui,control,Manager,Timer]

def restart():
   command = "/usr/bin/sudo shutdown -r now"
   #import subprocess
   process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
   output = process.communicate()[0]
   print (output)
   #print "restart called Demo"

def FixGPIO():
    try:
        subprocess.check_call(["sudo", "./enableGPIO.sh"])
        #if(VerifyTempSensor() == GPIO_ERROR):
            # if GPIO not working after enable owfs package - reset server
           # restart();
        
    except:
      print ("Exec error: ")

def ReStartApp():
    try:
      print ("running check processes") 
      process = CheckProcess()
      print (" pre=" + str(process))
      while process[0] > 0:  
        if(process[1] > 0):
            
            os.kill(int(process[1]), signal.SIGKILL)

            print (str(process[1]) + " was killed (Read Temp)")
        #    subprocess.check_call(["sudo","kill " + str(process[1])])
        if(process[2] > 0):
            os.kill(int(process[2]), signal.SIGKILL)
            print (str(process[2]) + " was killed (GUI)")
            #subprocess.check_call(["sudo","kill " + str(process[2])])
        if(process[3] > 0):
            os.kill(int(process[3]), signal.SIGKILL)
            print (str(process[3]) + " was killed (control)")
        if(process[4] > 0):
            os.kill(int(process[4]), signal.SIGKILL)
            print (str(process[4]) + " was killed (Manager)")
        if(process[5] > 0):
            os.kill(int(process[5]), signal.SIGKILL)
            print (str(process[5]) + " was killed (Manager)")
            #subprocess.check_call(["sudo","kill " + str(process[3])])
        process = CheckProcess()
      #subprocess.Popen(["sudo","/home/pi/Boiler/RunTempread.sh"])
      #print "read temp started"
      subprocess.Popen(["sudo","/home/pi/Boiler/Runboilercontrol.sh"])
      print ("Boiler control Started")
      #subprocess.Popen(["sudo","/home/pi/Boiler/runBoiler.sh"])
      #print "Boiler GUI started"
       


    except:
      print ("Exec error: ",sys.exc_info()[0])


# main
print ("*******" + str(datetime.datetime.now()) + "************")
print ("BoilerWd.py ....")
print ("verifying processes...")
process = CheckProcess()
print (str(process) )
if(process[0] != MANAGER_FLAG + TIMER_FLAG):
    print ("not all process are running  - restarting Apps")
    ReStartApp()
else:
    print ("All ok ")
    print ("verifying CPU usage for pid (" + str(process[2])+ ") ...")
    CPU = GetProcessCPU(process[2])
    if CPU > 40:
       print ("GUI CPU pid (" + str(process[2])+ ")is more then 40% verify once more before restart")
       time.sleep(2)
       CPU = GetProcessCPU(process[2])
       if CPU > 40:
           print (" CPU still High restarting process pid (" + str(process[2])  + ")")
           os.kill(int(process[2]), signal.SIGKILL)
           print (str(process[2]) + " was killed (GUI)")
           subprocess.Popen(["sudo","/home/pi/Boiler/runBoiler.sh"])
           print ("Boiler GUI Started")
   



