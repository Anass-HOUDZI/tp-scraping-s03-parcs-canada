from pathlib import Path

from src.exporter import export_to_jsonl
from src.parser import parse_places


SAMPLE_FILE = Path(
    "samples/sample_page.html"
)

OUTPUT_FILE = Path(
    "samples/sample_output.jsonl"
)

SOURCE_URL = (
    "https://parks.canada.ca/pn-np"
)


def main_verification() -> None:
    print(
        "=== VÉRIFICATION HORS-LIGNE ==="
    )

    if not SAMPLE_FILE.exists():
        print(
            f"ERREUR : fichier absent : "
            f"{SAMPLE_FILE}"
        )
        return

    html_content = SAMPLE_FILE.read_text(
        encoding="utf-8"
    )

    places = parse_places(
        html_content,
        SOURCE_URL,
    )

    seen_ids = set()
    valid_places = []

    rejected = 0
    duplicates = 0
    missing_fields = 0

    for place in places:
        missing = (
            place.missing_required_fields()
        )

        if missing:
            rejected += 1
            missing_fields += len(missing)
            continue

        if place.id in seen_ids:
            duplicates += 1
            rejected += 1
            continue

        seen_ids.add(place.id)
        valid_places.append(place)

    export_to_jsonl(
        valid_places,
        str(OUTPUT_FILE),
    )

    print(
        "Objets vus                    :",
        len(places),
    )
    print(
        "Objets exportés               :",
        len(valid_places),
    )
    print(
        "Objets rejetés                :",
        rejected,
    )
    print(
        "Doublons détectés             :",
        duplicates,
    )
    print(
        "Champs obligatoires manquants :",
        missing_fields,
    )

    normalization_ok = (
        bool(valid_places)
        and valid_places[0].url.startswith(
            "http"
        )
    )

    print(
        "URL absolue                   :",
        "OK"
        if normalization_ok
        else "ÉCHEC",
    )


if __name__ == "__main__":
    main_verification()