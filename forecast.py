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
    hourly = responses.Hourly()
    temperature = hourly.Variables(0).ValuesAsNumpy()
    humidity = hourly.Variables(1).ValuesAsNumpy()
    wind = hourly.Variables(2).ValuesAsNumpy()

    # Génère la timeline
    dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    df = pd.DataFrame({
        "Date": dates,
        "Température (°C)": temperature,
        "Humidité (%)": humidity,
        "Vent (km/h)": wind
    })

    return df




def main():
    # Localisation par défaut : Lomé
    #latitude = 6.13
    #longitude = 1.21

    print("📡 Récupération des données météo en cours...")
    params = coord_geo()
    response = forecast(params)
    df = process_data(response)

    print("✅ Données traitées. Aperçu :")
    print(df.head())

if __name__ == "__main__":
    main()


