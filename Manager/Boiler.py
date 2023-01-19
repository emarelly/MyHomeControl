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
			Minheatperiod = False
			CureItem = None
			time2heat = None
			manualitem = None
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
				MYTermo.ReadTemp(CureItem['mintemp'],CureItem['targettemp'],BoilerStatus) # read  temp from ESP module via rest api
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
						if self.CurretnShowers < CureItem['mintemp']: # if current temp les the min then turn on
							if BoilerStatus == 0:
								print (strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") is less than minimum (" + str(CureItem['mintemp']) + ") - turning the boiler on" )
								Boiler.SetRelay(Config.ControlRelayNum,1)
								BoilerStatus = 1
							else:
								print(strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") is less than minimum (" + str(CureItem['mintemp']) + ") - but boiler is already on" )
						elif self.CurretnShowers >= (CureItem['targettemp'] + Config.ThresholdFactor) and self.CurretnShowers >= (CureItem['mintemp'] + Config.ThresholdFactor):   # turn off if reached target value
							if BoilerStatus == 1:
								print (strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") reached target temp (" + str(CureItem['targettemp']) + ") turning the boiler off" )
								Boiler.SetRelay(Config.ControlRelayNum,0)
								BoilerStatus = 0
								Minheatperiod = False
							else:
								Minheatperiod = False
								print (strTime4Log +"Current temp (" + str(self.CurretnShowers) + ") reached target temp (" + str(CureItem['targettemp']) + ") boiler is already off" )
						elif Minheatperiod == False  : # calculate if when to turn on to get to the target on time
							time2heat = int(float(CureItem['targettemp']  - self.CurretnShowers) / (Config.HeatRate))
							print (strTime4Log + "time to heat " + str(time2heat) + "[Min]")
							time2start = CureItem['time2nextevent'] - time2heat
							if time2heat > 0 and BoilerStatus == 0:
								dt = CurrentDate + datetime.timedelta(minutes=time2start)
								print (strTime4Log + "Time To start Boiler (for now): " + dt.strftime('%Y-%m-%d %H:%M:%S %Z') )
							if time2start <= 0 and time2heat > 0: 
								if BoilerStatus == 0 :
									Boiler.SetRelay(Config.ControlRelayNum,1)
									BoilerStatus = 1
									Minheatperiod = True  # avoid on/off cycles during heating to target temp
									print (strTime4Log +"turning the boiler on to reach target temperature (current = " + str(self.CurretnShowers) + " target = " + str(CureItem['targettemp']))
								elif self.CurretnShowers >= (CureItem['mintemp'] + Config.ThresholdFactor):
									if BoilerStatus == 1 :
										Boiler.SetRelay(Config.ControlRelayNum,0)
										BoilerStatus = 0
									print (strTime4Log +"Current temp reached Min temp turning the boiler off" ) 
						else:
							if BoilerStatus == 0 :
								Boiler.SetRelay(Config.ControlRelayNum,1)
								BoilerStatus = 1        
							time2heat = int(float(CureItem['targettemp']  - self.CurretnShowers) / (Config.HeatRate))
							print (strTime4Log + "time to heat (while heating) " + str(time2heat) + "[Min]")
						#Update status class
						self.status.Date = CurrentDate
						self.status.MinVal = float(CureItem['mintemp'])
						if BoilerStatus==0: 
          					   self.status.HeaterOnOff ='Off'
						else: 
                  			           self.status.HeaterOnOff ='On'
						self.status.TargetVal = float(CureItem['targettemp'])
						self.status.TimeToStartMin = time2heat
						time.sleep(Config.SampleRateInSec)
		except:
			print("BoilerMonitor: " + traceback.format_exc())

