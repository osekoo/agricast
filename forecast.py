import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
#defintion de la zone georaphique
def coord_geo():
    latitude=input("Entrer la latitude du point")
    longitude=input("Entrer la longitude du point")
    params={
    "latitude":latitude,
    "longitude":longitude,
    "hourly":["temperature_2m","relative_humidity_2m","cloud_cover","wind_speed_10m"]
    }
    return params

#connection a l'API onpenmeteo et chargement des donnees metoe
def forecast(params):
    url="https://api.open-meteo.com/v1/forecast"
    #gestion de sesion et cache
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    #connection a l'API
    responses=openmeteo.weather_api(url,params=params)
    return responses[0]

#traitement des donnees meteo et conversion en dataframe
def process_data(responses):
    # Convertir les données en DataFrame
    df = pd.DataFrame(responses['hourly'])
    # Convertir les timestamps en datetime
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # Sélectionner les colonnes d'intérêt
    df = df[['time', 'temperature_2m', 'relative_humidity_2m', 'cloud_cover', 'wind_speed_10m']]
    return df

