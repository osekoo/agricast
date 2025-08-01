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

# definition des localites
Localites={
    "nom": ["Lomé", "Kpalimé", "Sokodé"],
    "latitude": [6.13, 6.90, 8.98],
    "longitude": [1.22, 0.63, 1.15],
    "prefecture": ["Maritime", "Plateaux", "Centre"],
    "region": ["Maritime", "Plateaux", "Centre"]
}

#enregistrement des localites au format json
def save_localites(localites, nom_fichier):
    localites_df = pd.DataFrame(localites)
    localites_df.to_json(nom_fichier, orient='records', lines=True)
    print(f"Localités saved to {nom_fichier}")
      

#fonction de chargement des localites depuis localites.json
def load_localites(nom_fichier):
    localites = pd.read_json(nom_fichier, lines=True)
    return pd.DataFrame(localites)

#fonction pour obtenir la meteo d'une localite a une date donnee

def get_meteo(localite, date):
    nom_fichier = "localites.json"
    url = "https://api.open-meteo.com/v1/forecast"
    #formatage de la date
    date = datetime.strptime(date, "%d-%m-%Y")
    date_str = date.strftime("%Y-%m-%d")
    #recuperation des coordonnees de la localite
    localites = load_localites(nom_fichier)
    latitude = localites.loc[localites["nom"] == localite, "latitude"].values[0]
    longitude = localites.loc[localites["nom"] == localite, "longitude"].values[0]
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': date_str,
        'end_date': date_str ,
        #'current_weather': 'true',
        'hourly': ['temperature_2m','rain','relative_humidity_2m','wind_speed_10m','cloud_cover']
    }
    response = openmeteo.weather_api(url, params=params)
    
    return response[0]


#traitement des donnees de meteo
def traitement_meteo(meteo):
    hourly = meteo.Hourly()
    temperature = hourly.Variables(0).ValuesAsNumpy()
    vent=hourly.Variables(3).ValuesAsNumpy()
    humidite=hourly.Variables(2).ValuesAsNumpy()
    nuage=hourly.Variables(4).ValuesAsNumpy()
    pluie=hourly.Variables(1).ValuesAsNumpy()
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
        "nuage": nuage,
        "pluie": pluie
    })
    return df