from meteo_metriques import load_localites,get_meteo_localite, traitement_meteo,save_localites
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

def main():

    # Localisation par défaut : Lomé
    #latitude = 6.13
    #longitude = 1.21
    #enregistrement des localites au format json
    Localites=save_localites("Localites.xlsx", "localites.json")

    #chargement  fichier localites.json sous forme de dataframe
    localites=load_localites(Localites)
    print(localites.head()) 

    # obtention de la meteo de lome le 25-07-2025
    meteo_lome= get_meteo_localite("Lomé", "25-07-2025", localites)
    print("📡 Récupération des données météo en cours...")

    df = traitement_meteo(meteo_lome)

    print("✅ Données traitées. Aperçu :")
    print(df.head())

if __name__ == "__main__":
    main()
