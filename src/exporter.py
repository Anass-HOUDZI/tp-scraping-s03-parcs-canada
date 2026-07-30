import json
import os

def export_to_jsonl(places: list, output_path: str = "samples/sample_output.jsonl"):
    """
    Prend une liste d'objets ProtectedPlace et l'exporte au format JSONL.
    Chaque ligne du fichier sera un objet JSON valide.
    """
    # S'assurer que le dossier de destination existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Mode 'w' pour écraser le fichier à chaque nouvelle exécution
    with open(output_path, 'w', encoding='utf-8') as f:
        for place in places:
            # Assure-toi que les caractères accentués (français) s'affichent bien
            json_line = json.dumps(place.to_dict(), ensure_ascii=False)
            f.write(json_line + '\n')
            
    print(f"✅ Export réussi : {len(places)} objets écrits dans {output_path}")