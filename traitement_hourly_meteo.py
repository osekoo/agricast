from openmeteo_sdk.Variable import Variable   
from datetime import datetime
def traitement_meteo(meteo):
    #enregistrement des donnees actuelles dans dictionnaire
    meteo_hourly=meteo.Hourly()

    #formatage de la date
    date = datetime.strptime(meteo_hourly.Time(), "%Y-%m-%dT%H:%M:%SZ")
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")   

    #extraction des variables meteos
    meteo_hourly_variables = list(map(lambda x: meteo_hourly.Variables(x), range(0,meteo_hourly.VariablesLength())))
    #extraction des valeurs des variables
    temperature_actuel = next(filter(lambda i: i.Variable()==Variable.temperature and i.Altitude()==2, meteo_hourly_variables),None)
    humidity_actuel = next(filter(lambda i: i.Variable()==Variable.relative_humidity and i.Altitude()==2, meteo_hourly_variables),None)
    wind_speed_actuel = next(filter(lambda i: i.Variable()==Variable.wind_speed and i.Altitude()==10, meteo_hourly_variables), None)
    cloud_cover_actuel = next(filter(lambda i: i.Variable()==Variable.cloud_cover and i.Altitude()==0, meteo_hourly_variables), None)    
    #mise en forme des donnees dans un dictionnaire
    meteo_dict = {
        "temperature": temperature_actuel.Value(),
        "humidity": humidity_actuel.Value() ,
        "wind_speed": wind_speed_actuel.Value(),
        "cloud_cover": cloud_cover_actuel.Value(),
        "time": date_str
    }
    return meteo_dict