#recupere les latitudes et longitudes des villes et le boundibox a partir du fichier localites.json
import pandas as pd
def get_localite(localite,nom_fichier):
    """prend la localite et le nom du fichier et retourne les coordonnees de la localite"""
    data_localites = pd.read_json(nom_fichier)
    #recuperation des coordonnees de la localite
    localite_data = data_localites.loc[data_localites['name'] == localite, ['latitude', 'longitude', 'bounding_box']]
    # si la localite n'est pas trouvee, retourne None
    if localite_data.empty:
        return None
    return localite_data.iloc[0].to_dict()

