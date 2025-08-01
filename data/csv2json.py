import csv
import json
import time

import requests

hdx_excluded_keys = ["ADM3_REF", "ADM3ALT1_FR", "ADM3ALT2_FR", "DATE", "VALIDON", "VALIDTO"]
hdx_key_translator = {
    "adm3_fr": "location_name",
    "adm3_pcode": "location_code",
    "adm2_fr": "prefecture_name",
    "adm2_pcode": "prefecture_code",
    "adm1_fr": "region_name",
    "adm1_pcode": "region_code",
    "adm0_fr": "country_name",
    "adm0_pcode": "country_code",
    "area_sqkm": "area"
}
osm_excluded_keys = ["place_id", "licence", "osm_type", "osm_id"]
osm_key_translator = {
    "lat": "latitude",
    "lon": "longitude",
    "addresstype": "address_type",
    "boundingbox": "bounding_box",
}

# Spécifiez les chemins d'accès de vos fichiers
csv_input_file = 'locations-tg.csv'
json_output_file = 'locations-tg.json'
full_output_file = 'locations-tg-full.json'
osm_missing_locations = 'locations-tg-missing.json'
# URL de base de l'API Nominatim (OSM)
nominatim_base_url = "https://nominatim.openstreetmap.org/search"


def csv_to_json(csv_filepath, json_filepath):
    """
    Lit un fichier CSV et le convertit en un fichier JSON.
    Chaque ligne du CSV devient un objet JSON.
    La première ligne du CSV est utilisée comme clés pour les objets JSON.

    Args:
        csv_filepath (str): Le chemin d'accès au fichier CSV d'entrée.
        json_filepath (str): Le chemin d'accès au fichier JSON de sortie.
    """
    data = []

    # Ouvre le fichier CSV en mode lecture avec l'encodage utf-8 pour éviter les erreurs
    with open(csv_filepath, 'r', encoding='utf-8') as csv_file:
        # Utilise DictReader pour lire chaque ligne comme un dictionnaire.
        # Les en-têtes de colonnes (première ligne) deviennent les clés.
        csv_reader = csv.DictReader(csv_file, delimiter=';')

        # Parcourt chaque ligne du lecteur CSV
        for row in csv_reader:
            # Crée un nouveau dictionnaire pour stocker les clés en minuscules
            lowercase_row = {hdx_key_translator[key.lower()]: value for key, value in row.items() if
                             key not in hdx_excluded_keys}

            names = lowercase_row['location_name'].split('/')
            for name in names:
                item = lowercase_row.copy()
                item['location_name'] = name.strip()
                data.append(item)

    # Ouvre le fichier JSON en mode écriture
    with open(json_filepath, 'w', encoding='utf-8') as json_file:
        # Écrit la liste de dictionnaires dans le fichier JSON.
        # indent=4 rend le fichier JSON lisible par un humain.
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def add_osm_coordinates_to_json(input_json_filepath, output_json_filepath):
    """
    Lit un fichier JSON, utilise Nominatim (OpenStreetMap) pour trouver
    les coordonnées GPS de chaque localité et enregistre les résultats
    dans un nouveau fichier JSON.

    Args:
        input_json_filepath (str): Le chemin d'accès au fichier JSON d'entrée
                                   (contenant la liste des localités).
        output_json_filepath (str): Le chemin d'accès au fichier JSON de sortie.
    """
    try:
        # Charger le fichier JSON existant
        with open(input_json_filepath, 'r', encoding='utf-8') as f:
            localities = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier d'entrée '{input_json_filepath}' n'a pas été trouvé.")
        return

    enriched_localities = []
    missing_localities = []
    headers = {
        'User-Agent': 'GeoData/OSM'
    }

    # Parcourir chaque localité dans la liste
    for i, locality in enumerate(localities):
        # Utiliser l'attribut 'adm1_fr' pour la recherche (ou un autre attribut si plus pertinent)
        locality_name = locality.get('location_name')
        country_code = locality.get('country_code')

        if not locality_name:
            print(f"Ligne {i + 1} : Clé 'location_name' non trouvée. Ignoré.")
            continue

        if not country_code:
            print(f"Ligne {i + 1} : Clé 'country_code' non trouvée. Ignoré.")
            continue

        print(f"Recherche des coordonnées pour : {locality_name}/{country_code}...")

        # Préparer les paramètres de la requête
        params = {
            'q': f"{locality_name}",  # Spécifier le pays pour plus de précision
            'countrycodes': f"{country_code.lower()}",
            'format': 'json'
        }

        try:
            # Envoyer la requête à l'API Nominatim
            response = requests.get(nominatim_base_url, params=params, headers=headers)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

            search_results = response.json()
            found_node = False
            for result in search_results:
                if result['osm_type'] == 'node':
                    found_node = True
                    new_locality = locality.copy()
                    for key, value in result.items():
                        if key not in osm_excluded_keys:
                            new_locality[osm_key_translator.get(key, key)] = value
                    enriched_localities.append(new_locality)

            if not found_node:
                missing_localities.append(locality)
                print(f"[ERROR] Aucun résultat trouvé pour : {locality_name}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Erreur de requête pour {locality_name} : {e}")


        # Respecter la limite d'utilisation de l'API Nominatim (1 requête/seconde)
        if i < len(localities) - 1:
            time.sleep(1)
        # break

    # Enregistrer la liste enrichie dans un nouveau fichier JSON
    with open(output_json_filepath, 'w', encoding='utf-8') as f:
        json.dump(enriched_localities, f, indent=4, ensure_ascii=False)

    with open(osm_missing_locations, 'w', encoding='utf-8') as f:
        json.dump(missing_localities, f, indent=4, ensure_ascii=False)

    print(f"\nTraitement terminé. Les données enrichies ont été enregistrées dans '{output_json_filepath}'.")


if __name__ == "__main__":
    try:
        csv_to_json(csv_input_file, json_output_file)
        print(f"Conversion réussie : '{csv_input_file}' a été transformé en '{json_output_file}'.")

        add_osm_coordinates_to_json(json_output_file, full_output_file)
        print(f"Récupération des données OSM réussie: ")
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{csv_input_file}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
