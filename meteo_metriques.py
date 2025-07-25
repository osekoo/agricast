import openmeteo_requests
import pandas as pd
import requests
from retry_requests import retry
from datetime import datetime   
from requests_cache import CachedSession    


#gestion de caches et de connexion a openmeteo
cache_session = CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url="https://api.open-meteo.com/v1/forecast"

#Enrengistrement des localites au format json
def save_localites(localites, str):
    localites= pd.read_excel(localites)
    localites.to_json(str, orient='records', lines=True)
    print(f"Localités saved to {str}")
    return str

#fonction de chargement des localites depuis localites.json
def load_localites(str):
    localites = pd.read_json(str,lines=True)
    return localites

#meteo de la localite
def get_meteo_localite(localite, date,data):
    #conversion de la date en format datetime
    date= datetime.strptime(date, "%d-%m-%Y")
    #formatage de la date pour l'API
    #date_str = date.strftime("%Y-%m-%d")
    date_str = date.strftime("%Y-%m-%d")
    #parametres de la requete
    #recuperation des coordonnees de la localite
    #localites=load_localites(str)
    params={
    "latitude":data.loc[data["nom"]==localite,]["latitude"],
    "longitude":data.loc[data["nom"]==localite,]["longitude"],
    "start":date_str,
    "end":date_str,
    "hourly":["temperature_2m","relative_humidity_2m","cloud_cover","wind_speed_10m"],
    "timezone":"Africa/Lome"
    }
    responses=openmeteo.weather_api(url,params=params)
    return responses[0]

#traitement des donnees de meteo
def traitement_meteo(meteo):
    hourly = meteo.Hourly()
    temperature = hourly.Variables(0).ValuesAsNumpy()
    vent=hourly.Variables(3).ValuesAsNumpy()
    humidite=hourly.Variables(1).ValuesAsNumpy()
    nuage=hourly.Variables(2).ValuesAsNumpy()
    dates = pd.date_range(
       start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
       end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
       freq=pd.Timedelta(seconds=hourly.Interval()),
       inclusive="left"
    )
    df = pd.DataFrame({
        "date": dates,
        "temperature": temperature,
        "vent": vent,
        "humidite": humidite,
        "nuage": nuage
    })
    return df