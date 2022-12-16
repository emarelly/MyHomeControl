from __future__ import print_function
import httplib2
import os
import sys
import datetime
import BoilerCalander
import TimerCalander
import json
import traceback
from datetime import timedelta
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
#CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API .NET'


class ReadGmailCalendar(object):
    """description of class"""
    secretPath = ""
    status = False
    def __init__(self,secret = ""):
         self.secretPath = secret
    def get_credentials(self):
        """Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        Returns:
            Credentials, the obtained credential.
        """
        cur_dir = os.getcwd() 
        credential_dir = os.path.join(cur_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'Calendar-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.secretPath, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def ReadCalendar(self):
        try:
            credentials = self.get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)

            Today = datetime.datetime.now()
            wd = Today.weekday()
            if wd == 6: # convert 0 = sunday 6 = Sat
                wd = 0
            else:
                wd = wd + 1
            TimeD = timedelta(weeks=0, days=wd, hours=Today.hour,minutes=Today.minute, seconds=Today.second,microseconds=Today.microsecond)
            StartTime = Today - TimeD
            EndTime = StartTime  + timedelta(weeks=1, microseconds=-1)
            print('Getting the upcoming weekly events')
            eventsResult = service.events().list(
                calendarId='primary', timeMin=StartTime.isoformat() + '+02:00',timeMax=EndTime.isoformat() + '+02:00', maxResults=100, singleEvents=True,
                orderBy='startTime').execute()
            events = eventsResult.get('items', [])
            if not events:
                print('No upcoming events found.')
            Boilertasks=[]
            Timertasks=[]
            for event in events:
                data = event['summary']
                strdate = event['start'].get('dateTime', event['start'].get('date'))
                #print('data is ' + data)
                ev = parseevent(data)
                if ev is None:
                    continue
                if  ev['type'] == 'Boiler':
                    date = datetime.datetime.strptime(strdate[0:len(strdate)-6],"%Y-%m-%dT%H:%M:%S")
                    if date.weekday() == 6 :
                        day = 1
                    else:
                        day = date.weekday() + 2
                    time = '{:02d}'.format(date.hour) + ":" + '{:02d}'.format(date.minute) + ":" + '{:02d}'.format(date.second) 
                    #print ('target  ' + str(ev['target']) + ' min =' + str(ev['min']))
                    btask = BoilerCalander.BoilerTask(dayOfWeek=day,hour = time,target=ev['target'],min=ev['min'])
                    Boilertasks.append(btask)
                    #start = event['start'].get('dateTime', event['start'].get('date'))
                elif ev['type'] == 'Timer':
                    date = datetime.datetime.strptime(strdate[0:len(strdate)-6],"%Y-%m-%dT%H:%M:%S")
                    if date.weekday() == 6 :
                        day = 1
                    else:
                        day = date.weekday() + 2
                    # add start event
                    #print('duration is ' + ev['duration'] + ' relay = ' + ev['relay'] + ' day = ' + str(day))
                    time = '{:02d}'.format(date.hour) + ":" + '{:02d}'.format(date.minute) + ":" + '{:02d}'.format(date.second) 
                    ttask = TimerCalander.TimerTask(dayOfWeek=day,hour = time,relaynum=ev['relay'],state=1)
                    Timertasks.append(ttask)
                    # add stop event
                    date = date + datetime.timedelta(seconds = int(ev['duration']))
                    time = '{:02d}'.format(date.hour) + ":" + '{:02d}'.format(date.minute) + ":" + '{:02d}'.format(date.second) 
                    ttask = TimerCalander.TimerTask(dayOfWeek=day,hour = time,relaynum=ev['relay'],state=0)
                    Timertasks.append(ttask)
                    #start = event['start'].get('dateTime', event['start'].get('date'))
                #print(start, event['summary'])
            bCalander = BoilerCalander.BoilerCalander(tasks=Boilertasks)
            tCalander = TimerCalander.TimerCalander(tasks=Timertasks)
            print(" read " + str(len(Boilertasks)) + " Boiler events")  
            print(" read " + str(len(Timertasks)) + " Timer events")  
            self.status = True
            print('read calendar done')
        except  :
            print("fail to ReadCalendar error: " + traceback.format_exc())
            #print ('fail to ReadCalendar error:' + str(sys.exc_info()[2]))
            bCalander = BoilerCalander.BoilerCalander()
            tCalander = TimerCalander.TimerCalander()
            self.status = False
        return [bCalander,tCalander]
                 
supported_astro = ['moonrise','moonset','dusk','dawn','sunset','sunrise','dusk','twilight','noon','midnight']
def parseevent(event):
    index = 0
    StartTime = []
    EndTime = []
    Offset = 0
    #print('parseevent: ' + event)
    if event.find('Boiler:')>= 0:
    #Bolier event
        args = list(filter(None, event.lower().replace('+',' + ').replace('-',' - ').replace('boiler:','').replace(';',' ').replace(',',' ').replace(':',' ').replace('=',' ').split(' ')))
        Target = None
        Min = None
        #print('found  ' + str(len(args)) + 'args' + str(args))
        while index < len(args):
            if args[index] == 'boiler':
                inbex += 1
                continue
            if args[index] == 'target':
                Target = args[index+1]
                index +=2
            if args[index] == 'min':
                Min = args[index+1]
                index +=2
            else:
                index +=1
        if Target is None or Min is None:
            return None
        else:
            return dict(type = 'Boiler',target=Target,min=Min)
    elif event.find('Timer:') >= 0	: # timer event
        args = list(filter(None, event.lower().replace('+',' + ').replace('-',' - ').replace('timer:','').replace(';',' ').replace(',',' ').replace(':',' ').replace('=',' ').split(' ')))
        RelayNumber = None
        Duration = None
        while index < len(args):
            if args[index] == 'timer':
                inbex += 1
                continue
            if args[index] == 'duration':
                Duration = args[index+1]
                index +=2
            elif args[index] == 'relaynum':
                RelayNumber = args[index+1]
                index +=2
            elif args[index] in supported_astro:
                value = args[index]
                if args[index+1] == '+':
                    Offset = int(args[index+2])
                    if Offset < 10:
                        offet = Offset * 60 # convert from hours to min 
                    index +=3
                elif args[index+1] == '-' :
                    Offset = -1 * int(args[index+2])
                    if Offset > -10:
                        offet = Offset * 60 # convert from hours to min 
                    index +=3
                else:
                    Offset = 0
                    index +=2
                if len(StartTime) == 0:
                    StartTime.extend([value,Offset])
                else:
                    EndTime.extend([value,Offset])
            else:
                index +=1
        if RelayNumber is None or (Duration is None and len(EndTime) == 0 ):
            return None
        else:
            return dict(type='Timer',Offset = Offset,relay = RelayNumber,duration = Duration, start = StartTime, end = EndTime )
    else:
        return None    