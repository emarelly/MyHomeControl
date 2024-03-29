import time
import os
import glob
import time
import signal
import datetime
import subprocess
import traceback # DEBUG
import datetime
import sys
import requests

OK = "OK"
APP_ERROR = "App error"

MANAGER_FLAG = 1
TIMER_FLAG = 100
            
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
        file = str(open(os.path.join('/proc', pid, 'cmdline'), 'rb').read())
        #print file
        if(file.count("BoilerManager.py")> 0):
	        count=count+MANAGER_FLAG
	        Manager = pid
            #print ("BoilerManager found")  
        if(file.count("TimerManager.py")> 0):
          count=count+TIMER_FLAG
          Timer = pid
          #print ("TimerManager found"  )
    except:
        print (traceback.format_exc())
  return [count,Manager,Timer]

def ReStartApp():
	try:
		print ("running check processes") 
		process = CheckProcess()
		print (" pre=" + str(process))
		while process[0] > 0:
			try:
				if(int(process[1]) > 0):
					os.kill(int(process[1]), signal.SIGKILL)
					print (str(process[1]) + " was killed (Manager)")
				if(int(process[2]) > 0):
					os.kill(int(process[2]), signal.SIGKILL)
					print (str(process[2]) + " was killed (Timer)")
				#subprocess.check_call(["sudo","kill " + str(process[3])])
				process = CheckProcess()
			except:
				print ("Exec iner error: "+  traceback.format_exc())
		subprocess.Popen(["sudo","/home/pi/Boiler/Runboilercontrol.sh"])
		print ("Boiler control Started")
	except:
		print ("Exec error: "+  traceback.format_exc())

def checkhttp(url):
  try:
    if requests.get(url).status_code == 200:
      return True
    else:
      return False 
  except:
    return  False
   
# main
print ("*******" + str(datetime.datetime.now()) + "************")
print ("BoilerWd.py ....")
print ("verifying processes...")
process = CheckProcess()
print (str(process) )
if(process[0] != MANAGER_FLAG + TIMER_FLAG or checkhttp('http://127.0.0.1:8000/status') == False):
    print ("not all process are running  - restarting Apps")
    ReStartApp()
else:
    print ("All ok ")
       



