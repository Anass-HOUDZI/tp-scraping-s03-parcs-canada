import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from config import OUTPUT_JSONL, SOURCE_URL
from src.parser import parse_park_detail


OUTPUT_FILE = Path(OUTPUT_JSONL)
EXPECTED_OBJECT_COUNT = 47


def display_result(
    control_name: str,
    success: bool,
    details: str = "",
) -> bool:
    """
    Affiche un résultat au format OK ou ECHEC.
    """

    status = "OK" if success else "ECHEC"
    print(f"{control_name} : {status}")

    if details:
        print(f"  {details}")

    return success


def load_jsonl(file_path: Path) -> list[dict]:
    """
    Charge un fichier JSONL sans effectuer de requête réseau.

    Chaque ligne non vide doit contenir un objet JSON valide.
    """

    objects = []

    with file_path.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Ligne JSON invalide à la ligne "
                    f"{line_number} : {error}"
                ) from error

            if not isinstance(item, dict):
                raise ValueError(
                    f"La ligne {line_number} ne contient "
                    "pas un objet JSON."
                )

            objects.append(item)

    return objects


def check_object_count(
    objects: list[dict],
) -> bool:
    """
    Contrôle 1 :
    vérifie que le fichier contient exactement 47 objets.
    """

    actual_count = len(objects)
    success = actual_count == EXPECTED_OBJECT_COUNT

    return display_result(
        "Contrôle 1 - nombre d'objets extraits",
        success,
        (
            f"Attendu : {EXPECTED_OBJECT_COUNT} | "
            f"Obtenu : {actual_count}"
        ),
    )


def is_absolute_http_url(value: object) -> bool:
    """
    Vérifie qu'une valeur est une URL HTTP ou HTTPS absolue.
    """

    if not isinstance(value, str):
        return False

    parsed_url = urlparse(value)

    return (
        parsed_url.scheme in {"http", "https"}
        and bool(parsed_url.netloc)
    )


def check_normalization(
    objects: list[dict],
) -> bool:
    """
    Contrôle 2 :
    vérifie les URLs absolues et les provinces en majuscules.
    """

    invalid_urls = []
    invalid_provinces = []

    for index, item in enumerate(
        objects,
        start=1,
    ):
        park_url = item.get("url")
        province = item.get("province")

        if not is_absolute_http_url(park_url):
            invalid_urls.append(index)

        if (
            not isinstance(province, str)
            or not province.strip()
            or province != province.upper()
        ):
            invalid_provinces.append(index)

    success = (
        not invalid_urls
        and not invalid_provinces
    )

    details = (
        f"URL absolues invalides : {len(invalid_urls)} | "
        f"Provinces non normalisées : "
        f"{len(invalid_provinces)}"
    )

    return display_result(
        "Contrôle 2 - normalisation des données",
        success,
        details,
    )


def check_duplicates_and_rejection(
    objects: list[dict],
) -> bool:
    """
    Contrôle 3 :
    vérifie l'absence de doublons et le rejet
    d'un objet incomplet.
    """

    object_ids = [
        item.get("id")
        for item in objects
        if item.get("id")
    ]

    duplicate_count = (
        len(object_ids)
        - len(set(object_ids))
    )

    incomplete_html = """
    <!DOCTYPE html>
    <html lang="fr">
        <head>
            <meta charset="utf-8">
        </head>
        <body>
            <main>
                <h1>Incomplete National Park</h1>
            </main>
        </body>
    </html>
    """

    incomplete_place = parse_park_detail(
        html_content=incomplete_html,
        page_url=(
            "https://parks.canada.ca/"
            "pn-np/ab/incomplete"
        ),
        source_url=SOURCE_URL,
        fallback_name="Incomplete National Park",
    )

    missing_fields = (
        incomplete_place.missing_required_fields()
    )

    rejection_success = (
        "summary" in missing_fields
    )

    success = (
        duplicate_count == 0
        and rejection_success
    )

    details = (
        f"Doublons détectés : {duplicate_count} | "
        "Objet incomplet rejeté : "
        f"{'oui' if rejection_success else 'non'}"
    )

    return display_result(
        "Contrôle 3 - déduplication et rejet",
        success,
        details,
    )


def main() -> int:
    """
    Exécute tous les contrôles hors ligne.
    """

    print("=" * 60)
    print("VÉRIFICATION HORS LIGNE DU SCRAPER PARCS CANADA")
    print("=" * 60)

    if not OUTPUT_FILE.exists():
        display_result(
            "Chargement du fichier de sortie",
            False,
            f"Fichier introuvable : {OUTPUT_FILE}",
        )

        print(
            "\nLance d'abord la collecte avec : "
            "python main.py"
        )

        return 1

    try:
        objects = load_jsonl(
            OUTPUT_FILE
        )
    except (OSError, ValueError) as error:
        display_result(
            "Chargement du fichier de sortie",
            False,
            str(error),
        )
        return 1

    results = [
        check_object_count(objects),
        check_normalization(objects),
        check_duplicates_and_rejection(objects),
    ]

    successful_controls = sum(results)
    total_controls = len(results)

    print("-" * 60)
    print(
        f"Résultat final : "
        f"{successful_controls}/{total_controls} "
        "contrôles réussis"
    )

    if all(results):
        print("Vérification terminée : OK")
        return 0

    print("Vérification terminée : ECHEC")
    return 1


if __name__ == "__main__":
    sys.exit(main())