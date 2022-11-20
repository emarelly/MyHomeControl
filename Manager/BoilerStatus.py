import time
import datetime 
import sys

class BoilerStatus (Object):
    def __init__(self):
        self.mStatus = 'off'
        self.mHeaterOnOff = 'No' 
        self.mDate = datetime.datetime.now()
        self.mMinVal = 0.0
        self.mTargetVal = 0.0 
        self.mTimeToStartMin = 0 
        self.mCurrentTemp = [-1,-1,-1] 
        self.mCurrentShowers = 0.0   
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)    
    def get_Status(self):
         	return self.mStatus
    def get_HeaterOnOff(self):
         	return self.mHeaterOnOff
    def get_Date(self):
         	return self.mDate
    def get_MinVal(self):
         	return self.mMinVal
    def get_TargetVal(self):
         	return self.mTargetVal
    def get_TimeToStartMin(self):
         	return self.mTimeToStartMin  
    def get_CurrentTemp(self):
         	return self.mCurrentTemp  
    def get_CurrentShowers(self):
         	return self.mCurrentShowers  
     
    def set_Status(self,a):
         	self.mStatus = a
    def set_HeaterOnOff(self,a):
         	self.mHeaterOnOff = a
    def set_Date(self,a):
         	self.mDate = a
    def set_MinVal(self,a):
         	self.mMinVal = a
    def set_TargetVal(self,a):
         	self.mTargetVal = a
    def set_TimeToStartMin(self,a):
         	self.mTimeToStartMin = a
    def set_CurrentTemp(self,a):
         	self.mCurrentTemp = a
    def set_CurrentShowers(self,a):
         	self.mCurrentShowers = a
     
    
    Status = property(get_Status, set_Status) 
    HeaterOnOff = property(get_HeaterOnOff, set_HeaterOnOff) 
    Date = property(get_Date, set_Date) 
    MinVal = property(get_MinVal, set_MinVal) 
    TargetVal = property(get_TargetVal, set_TargetVal) 
    TimeToStartMin = property(get_TimeToStartMin, set_TimeToStartMin) 
    CurrentTem = property(get_CurrentTem, set_CurrentTemn) 
    CurrentShowers = property(get_CurrentShowers, set_CurrentShowers) 
