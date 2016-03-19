"""
Date created: 12.3.2016
Author: Jiri Burant

First draft of the possible weather module package.
"""

#TODO: Get the forecast for next week,
#      Be able to get the weather from past
#      Select time period: Currently, Daily, Hourly


from urllib.request import Request, urlopen, URLError
from geopy.geocoders import Nominatim
import json
import datetime
    

def getLocation(place):
    geolocator = Nominatim()
    location = geolocator.geocode(place)
    return location

#init_hook initializes the class Weather
def init_hook(args):
    if ('town' in args):
        location=getLocation(args['town'])
        return Weather(location.latitude,location.longitude)
    else:
        return 'Error'

class Weather:
    def __init__(self, latitude, longitude):
        self.apikey='2fe3789874bc830a8cf2b1d98c4d7dbb' #Free apikey for up to 1000 queries per day, registered to the author
        self.latitude=latitude
        self.longitude=longitude

    def call_weather_api(self, latitude=self.latitude, longitude=self.longitude):
        request = Request('https://api.forecast.io/forecast/'+ self.apikey + '/' + str(latitude) +',' + str(longitude))
        print('calledWeather api')
            
        try:
            response = urlopen(request)
            data = json.loads(response.readall().decode('utf-8'))
        except URLError:
            data='There was an error'
            print ('Error')
         
        return data

    def convert_time(self, posixtime):
        return datetime.datetime.fromtimestamp(int(posixtime)).strftime('%Y-%m-%d %H:%M:%S')

    def get_summary(self,data,timeperiod='daily'):
        answer=data[timeperiod]['data'][0]['summary']
        return self.get_simplesentence(answer,'forecast says ')  

    def get_temperature(self,data,timeperiod='currently'):
        if(timeperiod=='currently'):
            answer=data[timeperiod]['data']['temperature']
            return self.get_simplesentence(answer,'temperature is ')  
        else:
            answer=data[timeperiod]['data'][0]['temperature']
            return self.get_simplesentence(answer,'temperature will be ')  
       
    def get_sunrise(self,data,timeperiod='daily'):
        time=convert_time(data[timeperiod]['data'][0]['sunriseTime']) 
        return self.get_simplesentence(time,'time of sunrise is ')  

    def get_sunset(self,data,timeperiod='daily'):
        time=convert_time(data[timeperiod]['data'][0]['sunsetTime'])
        return self.get_simplesentence(time,'time of sunset is ')
    
    def get_precip_intensity(self,data,timeperiod='currently'):
        if(timeperiod=='currently'):
            answer=data[timeperiod]['data']['precipIntensity']
            return self.get_simplesentence(answer,'intensity of the precipations is ')
        else:
            answer=data[timeperiod]['data'][0]['precipIntensity']
            return self.get_simplesentence(answer,'intensity of the precipations will be ')

    def get_humidity(self,data,timeperiod='currently'):
        if(timeperiod=='currently'):
            answer=data[timeperiod]['data']['humidity']
            return self.get_simplesentence(answer,'humidity is ')
        else:
            answer=data[timeperiod]['data'][0]['humidity']
            return self.get_simplesentence(answer,'humidity will be ')

    def get_windspeed(self,data,timeperiod='currently'):
        if(timeperiod=='currently'):
            answer=data[timeperiod]['windSpeed']
            return self.get_simplesentence(answer,'speed of wind is ')
        else:
            answer=data[timeperiod]['data'][0]['windSpeed']
            return self.get_simplesentence(answer,'speed of wind will be ')

    def get_moonphase(self,data,timeperiod='daily'):
        phase=double(data['daily']['data'][0]['moonPhase'])

        if(phase==0):
            answer='new moon'
        elif(phase==0.5):
            answer='full moon'
        elif(phase==0.25):
            answer='first quarter'
        elif(phase==0.75):
            answer='last quarter'
        elif(phase<0.25):
            answer='waxing crescent'
        elif(phase>0.25 and phase<0.5):
            answer='waxing gibbous'
        elif(phase>0.5 and phase<0.75):
            answer='wanning gibbous'
        elif(phase>0.75 and phase<1):
            answer='wanning crescent'

        return elf.get_simplesentence(answer,'moon phase is ')

    def get_temperatureMin(self,data,timeperiod='daily'):
        answer = data[timeperiod]['data'][0]['temperatureMin']
        return self.get_simplesentence(answer,'minimum temperature will be ')

    def get_temperatureMax(self,data,timeperiod='daily'):
        answer=data[timeperiod]['data'][0]['temperatureMax']
        return self.get_simplesentence(answer,'maximum temperature will be ')

    def get_visibility(self, data,timeperiod='currently'):
        if(timeperiod=='currently'):
            answer=data[timeperiod]['visibility']
            return self.get_simplesentence(answer,'visibility is ')
        else:
            answer=data[timeperiod]['data'][0]['visibility']
            return self.get_simplesentence(answer,'visibility will be ')
    
    #switcher serves as an intent switch, based on the intent, the appropriate actions are taken. The intents might change in the future
    switcher={'weather' : get_summary,
              'temperature': get_temperature,
              'sunrise': get_sunrise,
              'sunset': get_sunset,
              'precip':get_precip_intensity,
              'humidity':get_humidity,
              'windspeed':get_windspeed,
              'pressure':get_pressure,
              'moonphase':get_moonphase,
              'temperatureMin':get_temperatureMin,
              'temperatureMax':get_temperatureMax,
              'visibility':get_visibility,
              }

    #get_simplesentence returns the answer string, currently very simple
    def get_simplesentence(self,answer,intent):
        return 'The' + intent + answer

    def answersentence_add_location(self,answersentence,location):
        return answersentence+' in ' + location
        
    #Called from the query logic
    def query_resolution(self, intent, query ):
        location=''
        
        if (intent in self.switcher.keys()):
            
            if ('location' in query['entities']):    #If location is present in the query, take it into account
                location=query['entities']['location']['value']
                coordinates=getLocation(location)
                
                data=self.call_weather_api(coordinates.latitude,coordinates.longitude)
            else:
                data=self.call_weather_api()    #Use the default coordinates
             
            answersentence=self.switcher[intent](query,data)

            if(location!=''):
                answersentence=self.answersentence_add_location(answersentence,location)
        else:
            answersentence='query not recognised'

        return answersentence
