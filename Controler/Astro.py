import datetime
import astral
from geopy.geocoders import Nominatim


class addres:
    def __init__(self, streat,country='',number=0,city = '',state ='',timezone='',Name ='My pi homr contro'):
        self.streat  = streat
        self.number = number
        self.city = city
        if timezone == '':
            self.timezone = country
        else:
            self.timezone = timezone
        if(country == '' and state == ''):
           raise Exception("missig parameters - you must speficy state or country")
        if(country == ''):
            self.country = state
        elif (state == ''):
            self.country = country
        else:
            self.country = state + ', ' + country 
        
        if self.city != '':
            if self.streat != '':
                self.fulladderss = self.streat + ', ' + str(self.number) + ', ' + self.city +  ', ' + self.country
            else:
                self.fulladderss =  self.city + ', ' + self.country
        else:
            self.fulladderss = self.country
        # get cordinate by address
        geolocator = Nominatim(user_agent=Name)
        self.location = geolocator.geocode(self.fulladderss, timeout=None) 
    def GetLocation(self):
        return self.location
    def Observer(self):
        return astral.Observer(latitude= self.location.latitude,longitude= self.location.longitude)
def GetAstro(Astrotype,date,observer):
    if Astrotype == 'moonrise':
        return astral.moon.moonrise(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'moonset':
        return astral.moon.moonset(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'dusk':
        return astral.sun.dusk(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'dawn':
        return astral.sun.dawn(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'sunset':
        return astral.sun.sunset(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'sunrise':
        return astral.sun.sunrise(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'twilight':
        return astral.sun.twilight(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'midnight':
        return astral.sun.midnight(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    if Astrotype == 'noon':
        return astral.sun.noon(observer,date) + (datetime.datetime.now() - datetime.datetime.utcnow())
    return None

def Getmoonrise(dt,observer):
    astral.moon.moonrise(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getmoonset(dt,observer):
    astral.moon.moonset(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getdusk(dt,observer):
    astral.sun.dusk(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getdawn(dt,observer):
    astral.sun.dawn(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getsunset(dt,observer):
    astral.sun.sunset(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getsunrise(dt,observer):
    astral.sun.sunrise(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Gettwilight(dt,observer): # solar midnight
    astral.sun.twilight(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getmidnight(dt,observer):
    astral.sun.midnight(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
def Getnoon(dt,observer): # solar noon = highest point
    astral.sun.noon(observer,dt) + (datetime.datetime.now() - datetime.datetime.utcnow())
  
###### example  #########
##addr = addres(streat = 'hazamir',country='israel',city='ramat gan',timezone='jerusalem')
##dt = datetime.date.today()
##dawn = Getdown(dt,addr.Observer())
##################################