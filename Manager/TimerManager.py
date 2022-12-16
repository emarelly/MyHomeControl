import glob
import time
import array
import datetime 
import os.path
import controlrelay
import TimerCalander
import json
import traceback
import sys
import threading
import RealyMap
import Config

#TimerCalendarLocalPath = 'X:\Boiler\TimeCal.json'
#TimerManualLocalPath = 'E:\TimerProject\PiCode\TimerControler\manual.json'
#StatusFileName = 'E:\TimerProject\PiCode\TimerControler\temp.txt.current'

class Switch (object):
	def __init__(self,relynum):
           self.calevents = TimerCalander.TimerCalander()
           self.manualvent = TimerCalander.TimerCalander()
           self.relaynum = status
       
	@staticmethod
	def SetRelay(PortNum,PostValue,offsetport=1):
		
		if PostValue ==0:
			controlrelay.SetRelayOff(PortNum)
			if offsetport > 0:
				controlrelay.SetRelayOff(PortNum+offsetport)
		else:
			controlrelay.SetRelayOn(PortNum) 
			if offsetport > 0:
				controlrelay.SetRelayOn(PortNum+offsetport)   
	@staticmethod
	def GetNextEvent(calevents = None,sort = True ,relaynum = 3):
		retval = None
		try:  
			time2nextevent = -1
			duration = 0
			if calevents == None:
				return None
			else:
				CurrentDate = datetime.datetime.now() 
				currentTime = CurrentDate.time() 
				CurentDayOfWeek = CurrentDate.weekday() + 2
			if CurentDayOfWeek == 8 :
				CurentDayOfWeek = 1
			calevent = offsetcalander(calevents,CurentDayOfWeek)
			events = calevent.timerTasks
			nextevent = None
			eventafter = None
			#print ('found ' + str(len(events)))
			for event in events:
				#print(event.tostring())
				if event.relaynum != relaynum:
					#print ('not the same relay' + str(event.relaynum) + ' ' + str(relaynum))
					continue
				if event.dayOfWeek > 1 or (event.dayOfWeek == 1 and datetime.datetime.strptime(event.hour, '%H:%M:%S').time() > currentTime) :
					#print('next event =' + event.tostring())
					if nextevent == None:
						nextevent = event
					else:
						eventafter = event
						break
			if nextevent != None:
				relaynum = nextevent.relaynum
				state = nextevent.state
				thetime = datetime.datetime.strptime(str(CurrentDate.year) + '-' + str(CurrentDate.month) + '-' + str(CurrentDate.day) + ' ' + nextevent.hour, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=(event.dayOfWeek - 1))
				tdelta = thetime - CurrentDate
				time2nextevent = tdelta.seconds
				if eventafter != None:
					date2eventafter = datetime.datetime.strptime(str(CurrentDate.year) + '-' + str(CurrentDate.month) + '-' + str(CurrentDate.day) + ' ' + eventafter.hour, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=(event.dayOfWeek - 1))
					tdelta = date2eventafter - CurrentDate
					time2eventafter = tdelta.seconds 
				else:
					time2eventafter = 0
					date2eventafter = thetime
				retval = dict (time2nextevent= time2nextevent,  state=state ,  relaynum= int(relaynum), time2eventafter=time2eventafter,date2eventafter=date2eventafter)   
		except:
			print('GetNextEvent (relay  '+ str(relaynum)  + ') : '  + traceback.format_exc())
		return retval


	@staticmethod
	def offsetcalander(calevent,dayofweek):
           try:
             events = calevent.tasks(copy=True)
             for event in events:
                event.dayOfWeek -= (dayofweek-1)
                if event.dayOfWeek <= 0:
                   event.dayOfWeek += 7
             return TimerCalander.TimerCalander(events)
           except:
             print('offsetcalander exception '  + traceback.format_exc())
             return None

##  Main loop ####
##################


		# read XML #
	
	def TimerMonitor(self,relaynum):
		audit = None
		try:
			relaynum = self.relaynum
			
			CurrentDate = datetime.datetime.now() 
			strTime4Log = " " + datetime.datetime.ctime(CurrentDate) +  " : " 
			print (strTime4Log + "Starting Timer Monitor for relay " + str(relaynum) + " ....")
			auditfilename = Config.AuditFileName + str(relaynum) + '.log' 
			audit = open(auditfilename, "a")
			audit.write(strTime4Log + "Starting Timer Monitor for relay " + str(relaynum) + " ....")
			audit.flush()
			if os.path.exists(Config.TimerCalendarLocalPath):
				LastCalmodtime  = os.stat(Config.TimerCalendarLocalPath).st_mtime
				self.calevents.load(filename=Config.TimerCalendarLocalPath)
				mQuit = 1
				print ("last modified: %s" % time.ctime(LastCalmodtime).replace(':',"-").replace(' ',"_"))
			else:
				print (" file not found " + Config.TimerCalendarLocalPath)
				LastCalmodtime = None
				mQuit = 0
			if os.path.exists(str(relaynum)+Config.TimerManualLocalPath):
				self.manualvent = TimerCalander.TimerCalander()
				self.manualvent.load(filename=str(relaynum)+Config.TimerManualLocalPath)
				Lastmanualmodtime  = os.stat(str(relaynum)+Config.TimerManualLocalPath).st_mtime
			else:
				Lastmanualmodtime = None

		
			Minheatperiod = False
			CureItem = None
			while (mQuit == 1):
				# 
				CurrentDate = datetime.datetime.now() 
				currentTime = CurrentDate.time()
				strTime4Log = " " + datetime.datetime.ctime(CurrentDate) +  " : " 
				# read calendar & manual events #
				if os.path.exists(str(relaynum)+Config.TimerManualLocalPath):
					if Lastmanualmodtime == None or Lastmanualmodtime  != os.stat(str(relaynum)+Config.TimerManualLocalPath).st_mtime:
						if self.manualvent == None:
							self.manualvent = TimerCalander.TimerCalander()
						self.manualvent.load(filename=str(relaynum)+Config.TimerManualLocalPath)
						Lastmanualmodtime  = os.stat(str(relaynum)+Config.TimerManualLocalPath).st_mtime
				else:
					self.manualvent = None
				jsonmodtime  = os.stat(Config.TimerCalendarLocalPath).st_mtime
				if LastCalmodtime != jsonmodtime:
					self.calevents.load(filename=Config.TimerCalendarLocalPath)
					print (strTime4Log + "calendar file was changed, reading the updated Json")
					LastCalmodtime =  jsonmodtime
					print (strTime4Log + "last modified: %s" % time.ctime(jsonmodtime))
				manualitem = Switch.GetNextEvent(self.manualvent,True,relaynum)
				if manualitem == None and os.path.exists(str(relaynum)+Config.TimerManualLocalPath): # if manual command time finished remove the file
					os.remove(str(relaynum)+Config.TimerManualLocalPath)
					Lastmanualmodtime = None
				CureItem = manualitem or Switch.GetNextEvent(self.calevents,True,relaynum)
				RelayStatus = controlrelay.ReadRelay(int(relaynum))
				if CureItem == None:
					if RelayStatus == 1:
						SetRelay(int(relaynum),0) #in case of an error to read calander file turn off the realy
					time.sleep(Config.TimerSampleRateInSec)
					continue
				time2nexteventInMin = int(CureItem['time2nextevent']/60)
				ndt = CurrentDate + datetime.timedelta(minutes=time2nexteventInMin)
				print (strTime4Log +'current relay status= ' + str(RelayStatus) + ' Relay number = ' +  str(CureItem['relaynum']) + ' time to next event ' + str(CureItem['time2nextevent']) + ' state will be .. ' + str(CureItem['state'])+ '\n')
				if RelayStatus == int(CureItem['state']) and CureItem['time2nextevent'] > Config.TimerSampleRateInSec:
					print (strTime4Log +'relay status not in sync, Relay number = ' +  str(CureItem['relaynum']) + '\n')
					if RelayStatus == 1:
						audit.write(strTime4Log + 'switch #' + str(CureItem['relaynum']) + ' was turned off' + '\n')
						SetRelay(int(relaynum),0,0)
					else:
						audit.write(strTime4Log + 'switch #' + str(CureItem['relaynum']) + ' was turned on' + '\n')
						SetRelay(int(relaynum),1,0)
					audit.flush()
				elif CureItem['time2nextevent'] < Config.TimerSampleRateInSec:
					time.sleep(CureItem['time2nextevent'])
					print (strTime4Log +'relay status will be changed for relay ' +  str(CureItem['relaynum']) + '\n')
					if CureItem['state'] == '1':
						audit.write(strTime4Log + 'switch #' + str(CureItem['relaynum']) + ' was turned on' + '\n')
						SetRelay(int(relaynum),1,0)
					else:
						audit.write(strTime4Log + 'switch #' + str(CureItem['relaynum']) + ' was turned off' + '\n')
						SetRelay(int(relaynum),0,0)
					audit.flush()
					time.sleep(2)	
				else:
					if CureItem['time2eventafter'] > 0 and CureItem['time2eventafter'] < Config.TimerSampleRateInSec :
						if CureItem['time2eventafter'] > 2:
							time.sleep(CureItem['time2eventafter'] - 2)
					else:
						time.sleep(Config.TimerSampleRateInSec)
		except:
			audit.close()
			print(strTime4Log + "TimerMonitor for relay " + str(relaynum) + " : " + traceback.format_exc())
		
def runrealymonitor(threadsstatus,id):
    sw = Switch(id)
    sw.TimerMonitor(relaynum)
    threadsstatus[id] = -1 # if thread exit it becaue of error
    	
# main
threads = [] 
threadsstatus = 0 * [len(RealyMap.relaymap)]
events = TimerCalander.TimerCalander()
if(os.path.exists(Config.TimerCalendarLocalPath)): # read calander events json
    LastCalmodtime  = os.stat(Config.TimerCalendarLocalPath).st_mtime # marm file mod time
    events.load(filename=Config.TimerCalendarLocalPath)# load data
manualvents = TimerCalander.TimerCalander()
#start threads at first
for i in range(2,len(threadsstatus)):
    if Switch.GetNextEvent(events,True,i) is not None: # if calander include events for this switch -> start thread to process it
       	print ('starting thread ' + str (i))
        tr  = threading.Thread(target = runrealymonitor, args = [threadsstatus,str(i)])
        tr.start()
       	threads.append(tr)
       	threadsstatus[i] = tr.native_id    
    elif(os.path.exists(str(i)+Config.TimerManualLocalPath)):# manual calander created start thred to process it
        print ('starting thread for maual event ' + str (i))
        tr  = threading.Thread(target = runrealymonitor, args = [threadsstatus,str(i)])
        tr.start()
        threads.append(tr)
        threadsstatus[i] = tr.native_id
#monitor for new switches or restart exited threads 
modtime = None   
while(True):
	for i in range(2,len(threadsstatus)):
		# corner case
		if threadsstatus[i] < 0: # thread exit unexpectdly start it again
			print ('restarting thread ' + str (i))
			tr  = threading.Thread(target = runrealymonitor, args = [threadsstatus,str(i)])
			tr.start()
			threads.append(tr)
			threadsstatus[i] = tr.native_id    
		if threadsstatus[i] > 0: # active thread -> continue
			continue 
		if(os.path.exists(str(i)+Config.TimerManualLocalPath)): 
			# manual calander created start thred to process it
			print ('starting thread for maual event ' + str (i))
			tr  = threading.Thread(target = runrealymonitor, args = [threadsstatus,str(i)])
			tr.start()
			threads.append(tr)
			threadsstatus[i] = tr.native_id
		if(os.path.exists(Config.TimerCalendarLocalPath)): # look for new calander events if file was modified since last time
			modtime  = os.stat(Config.TimerCalendarLocalPath).st_mtime
			if LastCalmodtime != modtime:
				events.load(filename=Config.TimerCalendarLocalPath)
				print ("calendar file was changed, reading the updated Json")
				if Switch.GetNextEvent(events,True,i) is not None: #event exist for this swithc atart thread to process
       				   print ('starting thread ' + str (i))
        			   tr  = threading.Thread(target = runrealymonitor, args = [threadsstatus,str(i)])
        			   tr.start()
       				   threads.append(tr)
       				   threadsstatus[i] = tr.native_id  
	LastCalmodtime = modtime
	# thread list cleanup
	for x in range(len(threads)):
		if threads[x] is None | threads[x] =='':
			continue
		if threads[x].is_alive() == False:
			threads.pop(x)
			x= x-1

print ("exit Timer Monitor!!!")