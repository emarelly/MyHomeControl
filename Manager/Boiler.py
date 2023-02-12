import glob
import time
import array
import datetime 
import os.path
import json
import traceback
import sys
import ReadBoilerTemp
import controlrelay
import BoilerCalander
import BoilerStatus
import Config

     
class Boiler:
	# Generic Utiles
	#    
	def __init__(self,status):
		self.status = status
		self.CurrentTemp  = [-1,-1,-1]
		self.CurretnShowers = 0
    
	def GetCurrentTemp(self):	
         try:
            aList = ReadBoilerTemp.GetShowers()
            if aList[4] == -1:
                self.CurrentTemp  = [-1,-1,-1]
                self.CurretnShowers = -1
            else:
                self.CurrentTemp  = aList[0:3]
                self.CurretnShowers = aList[4]
         except:
            print ("GetCurrentTemp Exception")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print (''.join('!! ' + line for line in lines) ) # Log it or whatever hereprint "Unexpected error:", sys.exc_info()[0]      
            return [-1,1.0/120]
    
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
	def GetNextEvent(calevents = None,sort = True ):
		retval = None
		try:  
			time2nextevent = -1
			targettemp = 0
			mintemp = 0
			if calevents == None:
				return None
			#retval = {  'time2nextevent': time2nextevent,  'targettemp':targettemp ,  "mintemp": mintemp}
			else:
				CurrentDate = datetime.datetime.now() 
				currentTime = CurrentDate.time() 
				CurentDayOfWeek = CurrentDate.weekday() + 2
				if CurentDayOfWeek == 8 :
					CurentDayOfWeek = 1
				calevent = Boiler.offsetcalander(calevents,CurentDayOfWeek)
				events = calevent.boilerTasks
				nextevent = None
				for event in events:
					if event.dayOfWeek > 1 or (event.dayOfWeek == 1 and datetime.datetime.strptime(event.hour, '%H:%M:%S').time() > currentTime) :
						nextevent = event
						break
				if nextevent != None:
					targettemp = nextevent.target
					mintemp =  nextevent.min
					thetime = datetime.datetime.strptime(str(CurrentDate.year) + '-' + str(CurrentDate.month) + '-' + str(CurrentDate.day) + ' ' + nextevent.hour, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=(event.dayOfWeek - 1))
					tdelta = thetime - CurrentDate
					#tdelta = datetime.datetime.strptime(nextevent.hour, '%H:%M:%S').time() - currentTime
					time2nextevent = int(tdelta.seconds/60)
					retval = dict (time2nextevent= time2nextevent,  targettemp=float(targettemp) ,  mintemp= float(mintemp))   
		except:
			print("GetNextEvent: " + traceback.format_exc())
		return retval


	@staticmethod
	def offsetcalander(calevent,dayofweek):
		events = calevent.tasks(copy=True)
		for event in events:
		    event.dayOfWeek -= (dayofweek-1)
		    if event.dayOfWeek <= 0:
                       event.dayOfWeek += 7
		return BoilerCalander.BoilerCalander(events)

	def BoilerMonitor(self):
		try:
			# load calander files #
			calevents = BoilerCalander.BoilerCalander()
			manualvent = BoilerCalander.BoilerCalander()
			print ("Starting Boiler Monitor....")
			# mark json mod time #
			if os.path.exists(Config.CalendarLocalPath):
				LastCalmodtime  = os.stat(Config.CalendarLocalPath).st_mtime
				calevents.load(filename=Config.CalendarLocalPath)
				mQuit = 1
				print ("last modified: %s" % time.ctime(LastCalmodtime).replace(':',"-").replace(' ',"_"))
			else:
				print (" file not found " + Config.CalendarLocalPath)
				LastCalmodtime = None
				mQuit = 0
			if os.path.exists(Config.ManualLocalPath):
				manualvent = BoilerCalander.BoilerCalander()
				manualvent.load(filename=Config.ManualLocalPath)
				Lastmanualmodtime  = os.stat(Config.ManualLocalPath).st_mtime
			else:
				Lastmanualmodtime = None
			# read temp from ESP module and save it (overcome bug in the ESP controler of mult thread access)
			MYTermo = ReadBoilerTemp.Temp(60,Config.LogFileName,'http://ESPBoilerControler')
			# initial values befor loop
			CureItem = None
			time2heat = None
			manualitem = None
			OffForTarget = True
			OnForTarget = False
			while (mQuit == 1):
				BoilerStatus = controlrelay.ReadRelay(Config.ControlRelayNum)
				print(BoilerStatus)
				CurrentDate = datetime.datetime.now() #datetime.datetime.strptime("2015-06-07 00:01:00",'%Y-%m-%d %H:%M:%S') #datetime.datetime.now()
				currentTime = CurrentDate.time()
				strTime4Log = " " + datetime.datetime.ctime(CurrentDate) +  " : " #,"%a, %d %b %Y %H:%M:%S") +  " : "
				# read calendar & manual events #
				if os.path.exists(Config.ManualLocalPath):
					if Lastmanualmodtime == None or Lastmanualmodtime  != os.stat(Config.ManualLocalPath).st_mtime:
						manualvent = BoilerCalander.BoilerCalander()
						manualvent.load(filename=Config.ManualLocalPath)
						Lastmanualmodtime  = os.stat(Config.ManualLocalPath).st_mtime
					manualitem = Boiler.GetNextEvent(manualvent)	
				else:
					manualitem = None
				jsonmodtime  = os.stat(Config.CalendarLocalPath).st_mtime
				if LastCalmodtime != jsonmodtime:
					calevents.load(filename=Config.CalendarLocalPath)
					print (strTime4Log + "calendar file was changed, reading the updated Json")
					LastCalmodtime =  jsonmodtime
					print (strTime4Log + "last modified: %s" % time.ctime(jsonmodtime))
				
				if manualitem is None and os.path.exists(Config.ManualLocalPath): # if manual command time finished remove the file
					os.remove(Config.ManualLocalPath)
					Lastmanualmodtime = None
					manualvent = None
				if manualitem is not None:
					self.status.Status = 'Manual'
				else:
					self.status.Status = 'Auto'
				CureItem = manualitem or Boiler.GetNextEvent(calevents)
				if CureItem == None:
					print(strTime4Log + ' No Event To read' )
					time.sleep(Config.SampleRateInSec)
					continue
				# read temp from sensors
				MYTermo.ReadTemp(CureItem['mintemp'],CureItem['targettemp'],BoilerStatus) # read  temp from ESP module via rest api (parameters sent for audiig file in temp class)
				self.GetCurrentTemp()
				self.status.CurrentShowers = self.CurretnShowers
				self.status.CurrentTemp = self.CurrentTemp
				print ('current temp= ' + str(self.CurretnShowers) + ' MinTemp = ' +  str(CureItem['mintemp']) +  ' TargetTrmp = ' + str(CureItem['targettemp']))
				if  self.CurretnShowers == -1 :
					self.status.ActiveYesNo = 'No'
					self.status.Date = CurrentDate
					self.status.MinVal = 0.0
					self.status.Status = 'off'
					self.status.TargetVal = 0.0
					self.status.TimeToStartMin = 0
					print(strTime4Log + "Can't read temperature ")
				else:
						self.status.ActiveYesNo = 'Yes'
						MinTempOn = CureItem['mintemp']
						TargettempOn = CureItem['targettemp']
						MinTempOff = MinTempOn + Config.ThresholdFactor
						TargettempOff = TargettempOn + Config.ThresholdFactor
						#on flag
						time2heat = int(float(TargettempOn  - self.CurretnShowers) / (Config.HeatRate))
						time2startInMin = CureItem['time2nextevent'] - time2heat
						time2start = CurrentDate + datetime.timedelta(minutes=time2startInMin)
						if time2startInMin <= 0 and time2heat > 0: 
							OnForTarget = True #(e.g. turn on the heater)
						else:
							OnForTarget = False
						#off flag
						time2stopheat = int(float(TargettempOff  - self.CurretnShowers) / (Config.HeatRate))
						time2stopInMin = CureItem['time2nextevent'] - time2stopheat
						if time2stopInMin <= 0 and time2stopheat > 0: 
							OffForTarget = False #(e.g. Do not turn off the heater)
						else:
							if OffForTarget is False and self.CurretnShowers >= TargettempOff: # to avoid on off durig heating (when actual heat rate is greater then configured) turn off heater when heating started only if reached target
								OffForTarget = True

						if BoilerStatus == 0: # heater is currently off
							## must stay off
							## should be turned on
							if self.CurretnShowers < MinTempOn: # if current temp les the min then turn on
								Boiler.SetRelay(Config.ControlRelayNum,1)
								BoilerStatus = 1
								print (strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") is less than minimum (" + str(MinTempOn) + ") - turning the boiler on" )
							elif OnForTarget is True: # need to be started to get to target on time
									Boiler.SetRelay(Config.ControlRelayNum,1)
									BoilerStatus = 1
									print (strTime4Log +"turning the boiler on to reach target temperature (current = " + str(self.CurretnShowers) + " target = " + str(TargettempOn))								
							# status
							else: # print time to turn on status
									print (strTime4Log + "heating time " + str(time2heat) + "[Min]")						
									print (strTime4Log + "will start heatig @ " + str(time2start))						
						else: # heater is currently on
							## must stay on
							if self.CurretnShowers < MinTempOff: # if current temp les the min then keep on
								print(strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") is less than minimum (" + str(MinTempOff) + ") - but boiler is already on" )
							elif OffForTarget is False: # if current less then target keep on
								print (strTime4Log + "time left for heating " + str(time2heat) + "[Min]")								
							## should be off
							else:
								Boiler.SetRelay(Config.ControlRelayNum,0)
								BoilerStatus = 0
								if self.CurretnShowers >= MinTempOff : 
									print (strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") reached minimum temp (" + str(MinTempOff) + ") turning the boiler off" )
								else:
									print (strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") reached target (" + str(TargettempOff) + ") turning the boiler off" )
										
						#Update status class
						self.status.Date = CurrentDate
						self.status.MinVal = float(MinTempOn)
						if BoilerStatus==0: 
							self.status.HeaterOnOff ='Off'
						else: 
							self.status.HeaterOnOff ='On'
						self.status.TargetVal = float(TargettempOn)
						self.status.TimeToStartMin = time2startInMin
						time.sleep(Config.SampleRateInSec)
		except:
			print("BoilerMonitor: " + traceback.format_exc())

