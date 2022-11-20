import sys
import ftplib
import BoilerStatus
from ftplib import FTP

class NetworkConnection(object):
    """description of class"""
    hostname =""
    directory = ""
    username = ""
    password = ""
    ftp= None
    IsConnected = False
    statusfile = ""
    def __init__(self,hostname = "marellypi",directory = "//home//pi//Boiler", username="pi", password ="kerenm1", statusfilename = ""):
         self.hostname = hostname
         self.directory = directory
         self.username = username
         self.password = password
         self.statusfile = statusfilename

    def monitorPi(self):
       try:
            #self.ftp =FTP(host=self.hostname,passwd=self.password,user=self.username)
            #ftp.login() login doe when user and password provided
            #print("login succesful, current dir is:" + self.ftp.pwd())
            #self.IsConnected = True
            if(self.statusfile <> ""):
                #self.ftp.cwd(self.directory)
                if(self.ReadFile(fileName=self.statusfile)): # download file from remote pi
                    bstatus = BoilerStatus.BoilerStatus(self.statusfile)
                else:
                    bstatus = BoilerStatus.BoilerStatus("")
                    bstatus.strstatus = "can't read file"
       except  :
            print ('fail to connect to:' + self.hostname + " error:" + sys.exc_info()[1].message)
            bstatus = BoilerStatus.BoilerStatus("")
            bstatus.strstatus = "can't connect"
            IsConnected = False
       return bstatus      
    def ReadFile(self, fileName=""):
        status = False
        if self.IsConnected == False:
           try:
               self.ftp =FTP(host=self.hostname,passwd=self.password,user=self.username)
               #ftp.login() login doe when user and password provided
               print("login succesful, current dir is:" + self.ftp.pwd())
               self.IsConnected = True
              # return True
           except : 
              print ('fail to connect from:' + self.hostname + " error:" + sys.exc_info()[1].message)
              return
           try:
                self.ftp.cwd(self.directory)
                print 'Opening local file ' + fileName
                fs = open(fileName, 'wb') 
                self.ftp.retrbinary("RETR " + fileName, fs.write)
                print("read was succesful :" + fileName)
                status = True
           except: 
                print ('fail to read:' + fileName + " error:" + sys.exc_info()[1].message)
           #self.ftp.close()
           self.ftp.quit()
           self.IsConnected = False
           fs.close()
           return status
    def WriteFile(self, fileName=""):
        status = False
        if self.IsConnected == False:
           try:
               self.ftp =FTP(host=self.hostname,passwd=self.password,user=self.username)
               #ftp.login() login doe when user and password provided
               print("login succesful, current dir is:" + self.ftp.pwd())
               self.IsConnected = True
               #return True
           except:
              print ('fail to connect to:' + self.hostname)
           try:
                self.ftp.cwd(self.directory)
                print 'Opening local file ' + fileName
                fs = open(fileName, 'rb') 
                self.ftp.storbinary('STOR ' + fileName, fs)
                print("write was succesful :" + fileName)
                status = True
           except :
                print ('fail to write to:' + fileName + " error:" + sys.exc_info()[1].message)
           #self.ftp.close()
           self.ftp.quit()
           self.IsConnected = False
           fs.close()
           return status



