from traitement_hourly_meteo import traitement_meteo
from traitement_current_meteo import traitement_meteo
from get_meteo_1_1 import get_meteo
import get_localite
    

localite_chemin="agricast/data/locations-tg-full.json"

def main():
    print("📡 Récupération des données météo en cours...")

    meteo=get_meteo("Baguida", localite_chemin)
    
   # meteo lome actuel
    # Traitement des données météo
    df=traitement_meteo(meteo)
        
    print(df)

    #print("✅ Données traitées. Aperçu :")
    #print(meteo)  # Affiche les 24 premières heures
    
    # Enregistrement des données traitées dans un fichier json
    #df.to_json("meteo.json", orient='records', lines=True)
if __name__ == "__main__":
    main()
