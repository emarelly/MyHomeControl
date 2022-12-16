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
					os.kill(int(process[4]), signal.SIGKILL)
					print (str(process[4]) + " was killed (Manager)")
				if(int(process[2]) > 0):
					os.kill(int(process[5]), signal.SIGKILL)
					print (str(process[5]) + " was killed (Timer)")
				#subprocess.check_call(["sudo","kill " + str(process[3])])
				process = CheckProcess()
			except:
				print ("Exec iner error: "+  traceback.format_exc())
		subprocess.Popen(["sudo","/home/pi/Boiler/Runboilercontrol.sh"])
		print ("Boiler control Started")
	except:
		print ("Exec error: "+  traceback.format_exc())


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
       



