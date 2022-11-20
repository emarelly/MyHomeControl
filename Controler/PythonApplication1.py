
from __future__ import print_function
import httplib2
import os
import datetime
import BoilerCalander
import json
import ReadGmailCalendar
import NetworkConnection
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

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
    if isinstance(o, BoilerCalander.BoilerCalander):
        return o.tojson()

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    connect = NetworkConnection.NetworkConnection()
    #if connect.WriteFile("XMLFile1-ftp.xml"):
    #   print("ok")
    #else:
    #    print("fail")
    if connect.ReadFile("XMLFile1-ftp.xml"):
       print("ok")
    else:
        print("fail")
    Gcal = ReadGmailCalendar.ReadGmailCalendar(secret = CLIENT_SECRET_FILE)
    Bcal1 = Gcal.ReadCalendar()
    Bcal = BoilerCalander.BoilerCalander()
    Bcal.load('result.json')
    Bcal.save('resultafter.json')
    Bcal1 = BoilerCalander.BoilerCalander()
    Bcal1.load('result.json')
    if Bcal <> Bcal1:
        print("no")
if __name__ == '__main__':
    main()

