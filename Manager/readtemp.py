import time
import os
import glob
import time
#import Tkinter
import traceback # DEBUG
#import graph
#import Temp
import ReadBoilerTemp
#from Tkinter import *
# load the kernel modules needed to handle the sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
from datetime import date
import thread
import threading
def nothing():
   i=1
def threadwrap():
   # MYTermo = Temp(Frame)
  # time.sleep(0)
   time.sleep(5)
   # MYTermo.ShowTemp(Frame)
quit = 1
#root = Tkinter.Tk()
#stepTwo = Tkinter.LabelFrame(root, text="Control")
#stepTwo.grid(row=0, columnspan=7, sticky='W', \
#                 padx=5, pady=5, ipadx=100, ipady=10)
#stepOne = Tkinter.LabelFrame(root, text=" Current Temp ")
#scale = Tkinter.Scale(stepOne,from_=100,to=0,command=nothing)

#stepOne.grid(row=1, columnspan=7, sticky='W', \
#                 padx=5, pady=5, ipadx=55, ipady=55)
#root.title("Offek Gui Test")

#quitButton = Tkinter.Button(stepTwo, text="Quit", command=exit)
#quitButton.pack()
#tempbox = Tkinter.Label(stepOne)
#tempbox.pack()
#scale.pack()
LogFileName = "temp.txt"
if os.path.isfile(LogFileName):
  Lastmodtime  = os.stat(LogFileName).st_mtime
  BackupFileName = LogFileName + time.ctime(Lastmodtime).replace(':',"-").replace(' ',"_")
  os.rename(LogFileName,BackupFileName)
print (" calling readboiler ...")
MYTermo = ReadBoilerTemp.Temp(60,LogFileName,'http://192.168.14.108')
MYTermo.ReadTemp()
print ("done ...")
thread1 = threading.Thread(target=MYTermo.ShowTemp, args=() )
thread1.start()





