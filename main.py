from meteo_metriques import load_localites,get_meteo,save_localites,traitement_meteo
import openmeteo_requests
import pandas as pd
from retry_requests import retry
from datetime import datetime   
from requests_cache import CachedSession    


#gestion de caches et de connexion a openmeteo
cache_session = CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

nom_fichier="localites.json "

Localites={
    "nom": ["Lomé", "Kpalimé", "Sokodé"],
    "latitude": [6.13, 6.90, 8.98],
    "longitude": [1.22, 0.63, 1.15],
    "prefecture": ["Maritime", "Plateaux", "Centre"],
    "region": ["Maritime", "Plateaux", "Centre"]
}

def main():

    # Localisation par défaut : Lomé
    #latitude = 6.13
    #longitude = 1.21
    #enregistrement des localites au format json
    save_localites(Localites, nom_fichier)

    #chargement  fichier localites.json sous forme de dataframe
    #localites=load_localites(nom_fichier)
    #print(localites.head()) 

    # obtention de la meteo de lome le 25-07-2025
    meteo= get_meteo("Lomé", "31-07-2025")
    print("📡 Récupération des données météo en cours...")

   # meteo_lome.Hourly()

    df = traitement_meteo(meteo)

    print("✅ Données traitées. Aperçu :")
    print(df.head(24))  # Affiche les 24 premières heures
    print(meteo)
    # Enregistrement des données traitées dans un fichier json
    df.to_json("meteo.json", orient='records', lines=True)
if __name__ == "__main__":
    main()
