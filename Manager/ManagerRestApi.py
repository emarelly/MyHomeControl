from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import time
import json
import sys
import os.path
from itertools import islice
from collections import deque
import BoilerStatus
import BoilerCalander
import TimerCalander
from ManagerConfig import Config
# utils functions
# file head implmentatioin 
def head(filename,NOFlines=150): 
    if os.path.isfile(filename):
        with open("datafile") as myfile:
            head = list(islice(myfile, NOFlines))
        return str(head)
    else:
        return 'file not found'
#file tail implimentation
def tail(filename, NOFlines=150):
    if os.path.isfile(filename):
        with open(filename) as f:
            return str(deque(f, NOFlines))
    else:
        return 'file not found'
#generate manual calander file 
def genmanualcal(hours=3, temp=4,filename='manual.json'):
        CurrentDate = datetime.datetime.now() 
        currentTime = CurrentDate.time() 
        CurentDayOfWeek = CurrentDate.weekday() + 2
        if CurentDayOfWeek == 8 :
            CurentDayOfWeek = 1
        hr = currentTime.hour + hours
        if hr >= 24:
            hr = hr - 24
            CurentDayOfWeek += 1
        tmphr = ('0' + str(hr))[-2:] +':00:00'
        manual = BoilerCalander.BoilerCalander(tasks=[BoilerCalander.BoilerTask(dayOfWeek=CurentDayOfWeek,hour=tmphr,target=temp,min=temp)])
        manual.save(filename = filename)
 ## generate manual swithc jason
def genmanualcal4relay(duration=60, relay=2,filename='2Timemanual.json'):
        CurrentDate = datetime.datetime.now() 
        CurrentDate = CurrentDate + datetime.timedelta(seconds = 90)
        if CurrentDate.weekday() == 6 :
            day = 1
        else:
            day = CurrentDate.weekday() + 2
        time = '{:02d}'.format(CurrentDate.hour) + ":" + '{:02d}'.format(CurrentDate.minute) + ":" + '{:02d}'.format(CurrentDate.second) 
        ttask = TimerCalander.TimerTask(dayOfWeek=day,hour = time,relaynum=relay,state=1)
        Timertasks =[ttask]
        CurrentDate = CurrentDate + datetime.timedelta(seconds = int(duration))
        if CurrentDate.weekday() == 6 :
            day = 1
        else:
            day = CurrentDate.weekday() + 2
        time = '{:02d}'.format(CurrentDate.hour) + ":" + '{:02d}'.format(CurrentDate.minute) + ":" + '{:02d}'.format(CurrentDate.second) 
        ttask = TimerCalander.TimerTask(dayOfWeek=day,hour = time,relaynum=relay,state=0)
        Timertasks.append(ttask)
        manual = TimerCalander.TimerCalander(tasks=Timertasks)
        manual.save(filename = filename)
#http server wrapper class with shared status class 
class http_server:
    def __init__(self,ip,port, status):
        def handler(*args):
            BoilerRestHTTPRequestHandler(status, *args)
        self.server = HTTPServer((ip,port), handler)
    def serve_forever(self):
       self.server.serve_forever()

#request handler
class BoilerRestHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, status, *args):
        #print ('BoilerRestHTTPRequestHandler called')
        self.status = status
        BaseHTTPRequestHandler.__init__(self, *args)
       
    def do_GET(self):
        query = urlparse(self.path).query
        folder = urlparse(self.path).path.replace('/', '').lower()
        #if len(query) > 0:
        #    query_parameters = dict(qc.split("=") for qc in query.split("&"))
        if folder == 'status':
            out  = self.status.toJSON()
        elif folder == 'log': 
            out = 'log file is: \r\n' + tail('BoilerManager.log',150)
        else:
            out  = 'Hello, world! folder '  + folder
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(out.encode(encoding='utf-8', errors='strict'))
    
    def do_POST(self):
        query = urlparse(self.path).query
        folder = urlparse(self.path).path.replace('/', '').lower()
        if len(query) > 0:
            query_components = dict(qc.split("=") for qc in query.split("&"))
        if folder == 'updatecalander':
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            lines = self.rfile.read(content_length).decode('utf-8').splitlines()
            with open(Config.CalendarLocalPath,'w') as myfile:
                myfile.writelines(lines[3])
        elif folder == 'manualon':
            genmanualcal(hours=3, temp=4)
        elif folder == 'manualoff': 
            genmanualcal(hours=1, temp=0)
        elif folder == 'updaterelaycalander':
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            lines = self.rfile.read(content_length).decode('utf-8').splitlines()
            with open(Config.TimerCalendarLocalPath,'w') as myfile:
                myfile.writelines(lines[3])
        elif folder == 'relayon': 
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            lines = self.rfile.read(content_length).decode('utf-8').splitlines()
            data = json.loads(lines[0])
            genmanualcal4relay(duration==data['duration'],relay=data['swith'],filename=str(data['swith']) + Config.TimerManualLocalPath)
        elif folder == 'relayoff': 
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            lines = self.rfile.read(content_length).decode('utf-8').splitlines()
            data = json.loads(lines[0])
            genmanualcal4relay(duration==data['duration'],relay=data['swith'],filename=str(data['swith']) + Config.TimerManualLocalPath)
            genmanualcal4relay(duration==0,relay=data['swith'],filename=str(data['swith']) + Config.TimerManualLocalPath)
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def runserver(status):
    httpd = http_server('localhost', 8000, status)
    httpd.serve_forever()