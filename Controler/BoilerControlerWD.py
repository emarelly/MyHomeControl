import time
import os
import sys
import glob
import time
import signal
import datetime
import subprocess


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
  control = 0
  for pid in pids:
    try:
        file = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
        #print file
        if(file.count("BoilerControler.py") > 0):
          count=count+1
          control=pid
          print "found " + str(control)
    except:
        print "error get pid"
  return [count,control]

def restart():
   command = "/usr/bin/sudo shutdown -r now"
   #import subprocess
   process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
   output = process.communicate()[0]
   print output
   #print "restart called Demo"


def ReStartApp():
    try:
      print "running check process" 
      process = CheckProcess()
      print " pre=" + str(process)
      while process[0] > 0:  
        if(process[1] > 0):
            os.kill(int(process[1]), signal.SIGKILL)
            print str(process[1]) + " was killed (BoilerControler)"
        process = CheckProcess()
      subprocess.Popen(["sudo","/home/pi/BoilerControler/StartBoilerControler.sh"])
      print "Boiler control Started"
  
    except:
      print "Exec error: ",sys.exc_info()[0]


# main
print "*******" + str(datetime.datetime.now()) + "************"
print "verifying processes..."
process = CheckProcess()
print str(process) 
if(process[0] <> 2):
     print "not all process are running  - restarting app"
     ReStartApp()
else:
    print "All ok "
