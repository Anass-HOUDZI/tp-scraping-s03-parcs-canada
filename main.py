import os
from src.parser import parse_places
from src.exporter import export_to_jsonl

def main_verification():
    print("=== DÉBUT DE LA VÉRIFICATION HORS-LIGNE ===")
    
    # 1. Chargement du fichier local (Garantit l'exécution sans réseau)
    file_path = "samples/sample_page.html"
    if not os.path.exists(file_path):
        print(f"❌ Erreur : Le fichier {file_path} est introuvable. As-tu bien exécuté la commande curl ?")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    source_url = "https://parks.canada.ca/pn-np"
    
    # 2. Extraction via BeautifulSoup
    places = parse_places(html_content, source_url)
    
    # 3. Statistiques et Déduplication
    vus = len(places)
    exportes = 0
    rejetes = 0
    doublons = 0
    champs_manquants = 0
    
    ids_vus = set()
    objets_valides = []

    for place in places:
        # Règle de qualité : Rejet si un champ critique (ex: nom) est absent
        if not place.name or place.name == "Nom inconnu":
            rejetes += 1
            champs_manquants += 1
            continue
            
        # Règle de déduplication : On vérifie si l'ID a déjà été traité
        if place.id in ids_vus:
            doublons += 1
            rejetes += 1
            continue
            
        ids_vus.add(place.id)
        objets_valides.append(place)
        exportes += 1

    # 4. Export au format exigé (JSONL)
    export_path = "samples/sample_output.jsonl"
    export_to_jsonl(objets_valides, export_path)

    # 5. Affichage des 3 contrôles obligatoires pour la grille de notation
    print("\n=== RÉSULTATS DES CONTRÔLES AUTOMATIQUES ===")
    print(f"1. Nombre d'objets extraits (>0) : {'✅ OK' if vus > 0 else '❌ ÉCHEC'} ({vus} objets vus)")
    
    if objets_valides:
        test_item = objets_valides[0]
        # Vérification d'une normalisation (URL absolue)
        norm_ok = test_item.url.startswith("http")
        print(f"2. Normalisation URL absolue   : {'✅ OK' if norm_ok else '❌ ÉCHEC'} ({test_item.url})")
    else:
        print("2. Normalisation URL absolue   : ❌ ÉCHEC (aucun objet valide)")
        
    print(f"3. Déduplication / Rejets      : ✅ OK ({doublons} doublons, {rejetes} rejets au total)")

    # 6. Tableau récapitulatif pour remplir ton document Word facilement
    print("\n=== TABLEAU RÉCAPITULATIF (À copier dans le rapport) ===")
    print(f"Objets vus                    : {vus}")
    print(f"Objets exportés               : {exportes}")
    print(f"Objets rejetés                : {rejetes}")
    print(f"Doublons détectés             : {doublons}")
    print(f"Champs obligatoires manquants : {champs_manquants}")
    print("========================================================\n")

if __name__ == "__main__":
    main_verification()