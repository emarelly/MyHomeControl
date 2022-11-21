import os
import datetime
import time
import BoilerCalander
import TimerCalander
import json
import ReadGmailCalendar
import GmailMessages
import sys
import secrets
import traceback
import string
import remoteSSH
import requests
from ControlerConfig import Config
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
    if isinstance(o, BoilerCalander.BoilerCalander):
        return o.tojson()
    if isinstance(o, TimerCalander.TimerCalander):
        return o.tojson()


def Get(url):
    try:
        x = requests.get(url)
        return x.text
    except:
        return 'fail to get data'
    
def Post(url,filename=None,json=None):
    try:
        if filename is not None:
            myfiles = {'file': open(filename ,'rb')}
            x = requests.post(url, files = myfiles)
        elif json is not None:
            myobj = json
        else:
            myobj = {'somekey': 'somevalue'}
        x = requests.post(url, json = myobj)
        return x.text

    except:
        return 'fail to post data'
class ProcessControler(object):        
    prevcal = BoilerCalander.BoilerCalander()
    Timerprevcal = TimerCalander.TimerCalander()
    def __init__(self):
        #self.prevcal = BoilerCalander.BoilerCalander()
        self.prevcal.load(filename=Config.CalendarLocalPath)
        self.Timerprevcal.load(filename=Config.TimerCalendarLocalPath)
        self.two_factor_string = ''
        self.two_factor_related_command = ''
        self.two_factor_string_date = datetime.datetime.now()
        self.two_factor_failiure_count = 0
    def ValidateEmail(self, FromEmail="", AuthorizedEmailList =""):
     adresses = AuthorizedEmailList.lower().split(';')
     for email in adresses:
        if(FromEmail.lower().strip() == email.strip()):
           return True
     return False
    def generaterandomString(self,stringLength=10,relatedcommand = ''):
        rand = secrets.SystemRandom()
        self.two_factor_string = ''.join(string.ascii_lowercase[rand.randrange(0,len(string.ascii_lowercase))] for i in range(stringLength))
        self.two_factor_string_date = datetime.datetime.now()
        self.two_factor_related_command = relatedcommand

    def Processemail(self, mailclient):
        try:
            # etep 1 read incoming email (and delete after process)
           Msgs = mailclient.ReadMessages(delete=True)
           currentStatus = json.loads(Get(Config.GetStatusURL))
           for msg in Msgs:
               #verify that the emial is from authorized email adress 
                print('message received: ' + msg.subject)
                if (self.ValidateEmail(FromEmail =msg.Mailfrom, AuthorizedEmailList=Config.UserEmailList) ==True):
                    # mail tryp switch
                    #Boiler email optios
                    if (msg.subject.lower().find("status") >=0): # process mail for status request
                        currentStatus = json.loads(Get(Config.GetStatusURL))
                        # request for status send email back
                        if (currentStatus["Status"].lower() == "on"):
                                Body = 'Hello, \r\nThe boiler current status is: \r\n' + str(currentStatus) + "\r\n"
                                mailclient.SendMessage(MailSubect = "Bolier Service status", MailBody = Body, MailTo = msg.Mailfrom)
                        else:
                                Body = "Hello, \r\nThe boiler service is not active error " + str(currentStatus) + "\r\n"
                                mailclient.SendMessage(MailSubect = "Bolier Service status error", MailBody = Body, MailTo = msg.Mailfrom)
                    elif (msg.subject.lower().find("log") >=0):  # process mail for log request
                        resault = Get(Config.GetLogURL)
                        # request for status send email back
                        Body = "Hello, \r\nBoiler control log - last 150 lines: \r\n" + str(resault) + "\r\n"
                        mailclient.SendMessage(MailSubect = "Bolier Service log", MailBody = Body, MailTo = msg.Mailfrom)
                    # Timer email options
                    elif (msg.subject.lower().find("switch") >=0):
                        parts = msg.subject.lower().split(' ')
                        argv = []
                        for a in parts:
                            if a == '':
                                continue
                            argv.append(a)
                        print('processing message : ' + msg.subject)
                        if len(argv) < 2 or int(argv[1]) > 7 or int(argv[1]) < 2:
                            Body = 'incorrect value switch number must be 2 - 7 \n usage switch <switch number 2- 7> <duration in sec > 10 sec>' 
                            Subject = 'switch request error'
                        else:   
                            # request for status send email back
                            #resault = remoteSSH.runcommand(Config.BolilerControlerHostName,Config.USER,Config.PASS,22,'python /home/pi/Boiler/manualrelaynoff.py ' + argv[1])
                            #auditresault = remoteSSH.runcommand(Config.BolilerControlerHostName,Config.USER,Config.PASS,22,'cat /home/pi/Boiler/relayAudit' + argv[1]+'.log')
                            Body = 'Hello, \r\n' +  Get(Config.GetRelayStatusURL + argv[1])   #'Hello, \r\nThe switch status is ' + ''.join(resault) + '\r\n' + ''.join(auditresault) + '\r\n'
                            if len(argv) > 2:
                                print('2fk key going to be generated : ' )
                                self.generaterandomString(relatedcommand = 'switch ' + argv[1] + ' ' + argv[2]) 
                                print('2fk key generated : ' + self.two_factor_string)
                                Subject = self.two_factor_string
                            else:
                                Subject = 'switch status'
                        mailclient.SendMessage(MailSubect = Subject, MailBody = Body, MailTo = msg.Mailfrom)
                    elif (msg.subject.lower().find("on") >=0):
                        print('processing message : ' + msg.subject)                        
                        # request for status send email back
                        print('2fk key going to be generated : ' )
                        self.generaterandomString(relatedcommand = 'on') 
                        print('2fk key generated : ' + self.two_factor_string)
                        currentStatus = json.loads(Get(Config.GetStatusURL))
                        # request for status send email back
                        if (currentStatus["Status"].lower() == "on"):
                                #Body = "Hello, \r\nThe boiler current number of showers at " + currentStatus.date + " is: " + str(float(currentStatus.capacity[0]) / 10) + " ("+ str(currentStatus.capacity[1]) + "%) \r\nThe Boiler Heater is currently " + currentStatus.boilerrelay + "\r\n"
                                Body = 'Hello, \r\nThe boiler current status is: \r\n' + str(currentStatus) + "\r\n"
                                mailclient.SendMessage(MailSubect = "Bolier Service status", MailBody = Body, MailTo = msg.Mailfrom)
                        else:
                                Body = "Hello, \r\nThe boiler service is not active error " + str(currentStatus) + "\r\n"
                                mailclient.SendMessage(MailSubect = "Bolier Service status error", MailBody = Body, MailTo = msg.Mailfrom)
                    elif (msg.subject.lower().find("off") >=0):
                        print('processing message : ' + msg.subject)                        
                        # request for status send email back
                        print('2fk key going to be generated : ' )
                        self.generaterandomString(relatedcommand = 'off') 
                        print('2fk key generated : ' + self.two_factor_string)
                        currentStatus = json.loads(Get(Config.GetStatusURL))
                        # request for status send email back
                        if (currentStatus["Status"].lower() == "on"):
                                #Body = "Hello, \r\nThe boiler current number of showers at " + currentStatus.date + " is: " + str(float(currentStatus.capacity[0]) / 10) + " ("+ str(currentStatus.capacity[1]) + "%) \r\nThe Boiler Heater is currently " + currentStatus.boilerrelay + "\r\n"
                                Body = 'Hello, \r\nThe boiler current status is: \r\n' + str(currentStatus) + "\r\n"
                                mailclient.SendMessage(MailSubect = "Bolier Service status", MailBody = Body, MailTo = msg.Mailfrom)
                        else:
                                Body = "Hello, \r\nThe boiler service is not active error " + str(currentStatus) + "\r\n"
                                mailclient.SendMessage(MailSubect = "Bolier Service status error", MailBody = Body, MailTo = msg.Mailfrom)
                    elif (msg.subject.lower().find("reset") >=0):
                        print('processing message : ' + msg.subject)
                        currentStatus = json.loads(Get(Config.GetStatusURL))
                        # request for status send email back
                        print('2fk key going to be generated : ' )
                        self.generaterandomString(relatedcommand = 'reset') 
                        print('2fk key generated : ' + self.two_factor_string)
                        if (currentStatus.date != ""):
                                Body = "Hello, \r\nThe boiler current number of showers at " + currentStatus.date + " is: " + str(float(currentStatus.capacity[0]) / 10) + " ("+ str(currentStatus.capacity[1]) + "%) \r\nThe Boiler Heater is currently " + currentStatus.boilerrelay + "\r\n"
                        else:
                                Body = "Hello, \r\nThe boiler service is not active error " + currentStatus.strstatus + "\r\n"
                        mailclient.SendMessage(MailSubect = self.two_factor_string, MailBody = Body, MailTo = msg.Mailfrom)
                    #2FA return code - validate and perform the change
                    elif (len(self.two_factor_string) >= 10 and msg.subject.find(self.two_factor_string) >=0):
                        # 2 factor athentication confirmed perform the request.
                        # valdate token expiration time first
                        if  (datetime.datetime.now() - self.two_factor_string_date).seconds < 120 and self.two_factor_failiure_count < Config.MaxFailures:
                            self.two_factor_failiure_count = 0
                            #turn switch sycle
                            if self.two_factor_related_command.lower().find('switch') >=0:
                                argv = self.two_factor_related_command.lower().split(' ')
                                Post(Config.PostUpdateManualRelayOnURL,json={"swith": int(argv[1]),"duration":int(argv[2])})
                            # turn boiler on
                            if self.two_factor_related_command.lower().find('on') >=0:
                                Post(Config.PostUpdateManualCalOnURL)
                            # turn boiler off
                            if self.two_factor_related_command.lower().find('off') >=0:
                                Post(Config.PostUpdateManualCalOffURL)
                             # turn reset bolier manager pi
                            if self.two_factor_related_command.lower().find('reset') >=0:
                                remoteSSH.runcommand(Config.BolilerControlerHostName,Config.USER,Config.PASS,22,'sudo reboot')
                            self.two_factor_related_command = ''
                            Body = "Hello, \r\nThe request was done \r\n"
                            mailclient.SendMessage(MailSubect = "The request done", MailBody = Body, MailTo = msg.Mailfrom)
                        else:
                            self.two_factor_failiure_count += 1
                            Body = "Hello, \r\nThe request token expired\r\n"
                            self.two_factor_related_command = ''
                            mailclient.SendMessage(MailSubect = "The request token expired or reached max retry", MailBody = Body, MailTo = msg.Mailfrom)
        except:
            print("processmail: " + traceback.format_exc())
    def ProcessCalendar(self,calclient, mailclient):
        #boiler Calendar
        currentcal = calclient.ReadCalendar()
        currentBoilercal = currentcal[0]
        print ('ProcessCalendar: processing Boiler Calendar')
        if(calclient.status == False):
            mailclient.SendMessage(MailSubect ="Fail to read Calander",  MailBody = "Hello,\r\nFail to read boiler calander fro gmail", MailTo = Config.AdminEmailList)
            skip=True
        skip=False
        if (self.prevcal.len() == 0 and currentBoilercal.len() > 0):
            mailclient.SendMessage(MailSubect ="Boiler Calander was created",  MailBody = "Hello,\r\nThe Boiler Calander was created", MailTo = Config.AdminEmailList)
        elif (self.prevcal != currentBoilercal):
            mailclient.SendMessage(MailSubect ="Boiler Calander was modified", MailBody ="Boiler Calander was modified as follows: \r\n" + self.prevcal.diff(other_cal = currentBoilercal) ,MailTo = Config.AdminEmailList)
        else: # no change skip
            skip=True 
        if skip == False:
            self.prevcal = currentBoilercal
            self.prevcal.save(filename=Config.CalendarLocalPath)
            Post(Config.PostUpdateCalURL,Config.CalendarLocalPath) # update json file via rest api post
        print ('ProcessCalendar: processing Timer Calendar')
        currentTimercal = currentcal[1]
        if(calclient.status == False):
            mailclient.SendMessage(MailSubect ="Fail to read Calander",  MailBody = "Hello,\r\nFail to read Timer calander fro gmail", MailTo = Config.AdminEmailList)
        if (self.Timerprevcal.len() == 0 and currentTimercal.len() > 0):
            mailclient.SendMessage(MailSubect ="Timer Calander was created",  MailBody = "Hello,\r\nThe Timer Calander was created", MailTo = Config.AdminEmailList)
        elif (self.Timerprevcal != currentTimercal):
            mailclient.SendMessage(MailSubect ="Timer Calander was modified", MailBody ="Timer Calander was modified as follows: \r\n" + self.Timerprevcal.diff(other_cal = currentTimercal) ,MailTo = Config.AdminEmailList)
        else: # no change exit
            return 
        print ('ProcessCalendar: saving to prev')  
        self.Timerprevcal = currentTimercal
        # UpdateJson
        Post(PostUpdateRelayURL,filename=Config.TimerCalendarLocalPath)
        return 
            



def main():
        print("Phyton Controler: started")
        Mailclient = GmailMessages.GmailMessages(Config.CLIENT_SECRET_FILE)
        CalClient =  ReadGmailCalendar.ReadGmailCalendar(Config.CLIENT_SECRET_FILE)
        process = ProcessControler()
        #resault = Mailclient.SendMessage(MailSubect ="Bolier Phyton Service was started", MailBody = "I am up Now :)",MailTo = Config.AdminEmailList)
        Pistatus = json.loads(Get(Config.GetStatusURL))
        keepaliveCount = 0
        KeepAlivefactor = 3600/ Config.RefreshTime # keep alive every hour on when need to change status
        while (True):
           try:
               #Validate pi status
               if keepaliveCount > KeepAlivefactor:
                     keepaliveCount = keepaliveCount +1
                     print('monitor status test at '+ datetime.datetime.now().isoformat())
                     Pistatus = json.loads(Get(Config.GetStatusURL))
                     if Pistatus['status'].lower() != 'on':
                                keepaliveCount = 0
                                count= count + 1
                                # if pi is down send email alert to admin
                                if (count > 3):
                                    Mailclient.SendMessage(MailSubect = "PI is not working", MailBody= "Hello, \r\n the pi is curently not working please look into it. reported error is: " + str(Pistatus),MailTo = Config.AdminEmailList)
                                    count = 0
                                    keepaliveCount = 0
                                else:
                                   print("fail to monitor:" + str(count) + " times ")
                           
                     else:
                       keepaliveCount = 0
               if(Pistatus['status'].lower() == 'on'):
                            count = 0
                            # Process email requests
                            process.Processemail(mailclient = Mailclient)
                            # Process Calendar events
                            process.ProcessCalendar(calclient = CalClient, mailclient = Mailclient)
               else:
                           Pistatus = json.loads(Get(Config.GetStatusURL))
                           if (Pistatus['status'].lower() == 'on'):
                                Mailclient.SendMessage(MailSubect = "Connection to PI restored",MailBody= "Hello, \r\n The connection to pi was restored.",MailTo = Config.AdminEmailList)
                
           except  :
               print ('main loop Exception error:' + sys.exc_info()[1].message)
           time.sleep(Config.RefreshTime) 

    

if __name__ == '__main__':
    main()








