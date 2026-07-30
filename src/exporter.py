import json
import os


def export_to_jsonl(
    places: list,
    output_path: str = "samples/sample_output.jsonl",
):
    """
    Prend une liste d'objets ProtectedPlace et l'exporte
    au format JSONL.

    Chaque ligne du fichier contient un objet JSON valide.
    """

    # Récupère le dossier du fichier de sortie
    output_directory = os.path.dirname(output_path)

    # Crée le dossier uniquement s'il existe dans le chemin
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    # Le mode "w" écrase le fichier à chaque exécution
    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        for place in places:
            json_line = json.dumps(
                place.to_dict(),
                ensure_ascii=False,
            )

            file.write(json_line + "\n")

    print(
        f"✅ Export réussi : {len(places)} objets "
        f"écrits dans {output_path}"
    )