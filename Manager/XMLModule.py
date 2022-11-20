import xml.etree.ElementTree as ET
import glob
import time
import array
import datetime 
import os.path


class StatusItem(object):
    mDate = datetime.MINYEAR
    mTime = datetime.time.min
    mMinVal = 0
    mTargetVal = 0
    
    def __init__(self, *args, **kwargs):
     self.mDate = args[0]
     self.mTime2Active = args[1]
     self.mMinVal =args[2]
     self.mTargetVal = args[3]
  
class XMLStatusHandler(object):  
  mFileName = ""
  def __init__(self, *args, **kwargs):
     self.mFileName = args[0]
  
  def GetXMLData(self):
    try:  
        print ("GetXMLData")
         # File Modification time in seconds since epoch
        file_mod_time = round(os.stat(self.mFileName).st_mtime)
         # Time in seconds since epoch for time, in which logfile can be unmodified.
        t = datetime.datetime.today() - datetime.timedelta(minutes=30)
        should_time = round(time.mktime(t.timetuple()))
         # Time in minutes since last modification of file
        last_time = round((int(time.time()) - file_mod_time) / 60, 2)
        if (file_mod_time - should_time) < 20:
          xi= StatusItem(datetime.MINYEAR,datetime.time.min,-1,-1)
          aList = [xi]
          print ("CRITICAL:", self.mFileName, "last modified", last_time, "minutes. Threshold set to 20 minutes")
          return aList
        else:
           print ("OK. Command completed successfully for ", self.mFileName, " ", last_time, "minutes ago.")
  
        tree = ET.parse(self.mFileName)
        root = tree.getroot()
        aList = []
        # pars XML and build event list
        for  leaf in root.findall('status'):
          xDate = leaf.find('TargetDate').text
          xtime2Active = leaf.find('TimeToStart').text
          MinVal = leaf.find('MinVal').text
          TargetVal = leaf.find('TargetVal').text
          #print "step2"
          #print day, time , MinVal, TargetVal
          aList.append(StatusItem(datetime.datetime.strptime(xDate,'%Y-%m-%d %H:%M:%S'),datetime.datetime.strptime(xtime2Active,'%Y-%m-%d %H:%M:%S'),float(MinVal),float(TargetVal)))
        # sort by 
        #print "step4"
        return aList 
    except:
        print ("CRITICAL:", self.mFileName, "not found")
        xi= StatusItem(datetime.MINYEAR,datetime.time.min,-1,-1)
        aList = [xi]
        return aList 
    
  def WriteXMLData (self, nList):
    try:
      f = open(self.mFileName,'w')
      f.write('<data> \n')
      for x,item in enumerate(nList):
            f.write('<status Name="' + str(x) +'"> \n')
            f.write('<TargetDate>' + item.mDate.strftime('%Y-%m-%d %H:%M:%S') + '</TargetDate>\n')
            f.write('<TimeToStart>' + item.mTime2Active.strftime('%Y-%m-%d %H:%M:%S') + '</TimeToStart>\n')
            f.write('<MinVal>' + str(item.mMinVal) + '</MinVal>\n')
            f.write('<TargetVal>' + str(item.mTargetVal) + '</TargetVal>\n')
            f.write('</status>')
      f.write('</data> \n')
      f.close()
    except:
        print ("CRITICAL:", self.mFileName, "error writing to file")
