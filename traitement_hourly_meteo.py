from openmeteo_sdk.Variable import Variable   
from datetime import datetime
import numpy as np
import pandas as pd
def traitement_meteo_hour(meteo):
    #enregistrement des donnees actuelles dans dictionnaire
    meteo_hourly=meteo.Hourly()

    #formatage de la date
    hourly_time = range(meteo_hourly.Time(), meteo_hourly.TimeEnd(), meteo_hourly.Interval())
    date= pd.to_datetime(hourly_time, unit='s', utc=True)
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")   

    #extraction des variables meteos
    meteo_hourly_variables = list(map(lambda x: meteo_hourly.Variables(x), range(0,meteo_hourly.VariablesLength())))
    #extraction des valeurs des variables
    temperature_hour = next(filter(lambda i: i.Variable()==Variable.temperature and i.Altitude()==2, meteo_hourly_variables),None).ValuesAsNumpy()
    humidity_hour = next(filter(lambda i: i.Variable()==Variable.relative_humidity and i.Altitude()==2, meteo_hourly_variables),None).ValuesAsNumpy()
    wind_speed_hour = next(filter(lambda i: i.Variable()==Variable.wind_speed and i.Altitude()==10, meteo_hourly_variables), None).ValuesAsNumpy()
    cloud_cover_hour = next(filter(lambda i: i.Variable()==Variable.cloud_cover and i.Altitude()==0, meteo_hourly_variables), None).ValuesAsNumpy()    
    #mise en forme des donnees dans un dictionnaire
    hourly_data = {"date": pd.date_range(
    start = pd.to_datetime(meteo_hourly.Time(), unit = "s"),
    end = pd.to_datetime(meteo_hourly.TimeEnd(), unit = "s"),
    freq = pd.Timedelta(seconds = meteo_hourly.Interval()),
    inclusive = "left"
                 )}
    meteo_dict = {
        "temperature": temperature_hour,
        "humidity": humidity_hour,
        "wind_speed": wind_speed_hour,
        "cloud_cover": cloud_cover_hour,
        "time": date_str,
    }
    return meteo_dict