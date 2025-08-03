from get_localite import get_localite
import openmeteo_requests
from retry_requests import retry
from datetime import datetime   
from requests_cache import CachedSession

#gestion de caches et de connexion a openmeteo
cache_session = CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def get_meteo(localite,nom_fichier):
    """prend la localite et le nom du fichier et retourne la meteo de la localite
    """
    url= "https://api.open-meteo.com/v1/forecast"

    #cooerdonnees de la localite
    localite_data = get_localite(localite, nom_fichier)
    if localite_data is None:
        raise ValueError(f"Localité '{localite}' non trouvée dans le fichier {nom_fichier}.")
    latitude = localite_data['latitude']
    longitude = localite_data['longitude']
    bonding_box = localite_data.get('bounding_box', None)
    #parametres de la requete
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'cloud_cover'],
        'timezone': 'Africa/Lome',
        'hourly': ['temperature_2m', 'rain', 'relative_humidity_2m', 'wind_speed_10m', 'cloud_cover'],
        'daily': ['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum', 'sunrise', 'sunset'],
        #'bounding_box': bonding_box if bonding_box else None
    }
    #requete a l'api openmeteo
    try:
        response = openmeteo.weather_api(url, params=params)
    except Exception as e:
        print(f"Erreur lors de la récupération des données météo pour {localite}: {e}")
        return None
    return response[0]