from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from config import SAMPLE_JSONL, SOURCE_URL
from src.models import ProtectedPlace
from src.parser import parse_park_links

SAMPLE_PAGE = Path("samples/sample_page.html")
SAMPLE_OUTPUT = Path(SAMPLE_JSONL)
MAX_OBJECTS = 60


def load_jsonl(path: Path) -> list[dict]:
    objects: list[dict] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, raw in enumerate(file, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"JSON invalide ligne {line_number}: {error}") from error
            if not isinstance(item, dict):
                raise ValueError(f"La ligne {line_number} n'est pas un objet JSON")
            objects.append(item)
    return objects


def is_absolute_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def as_place(item: dict) -> ProtectedPlace:
    return ProtectedPlace(
        id=item.get("id", ""),
        name=item.get("name"),
        province=item.get("province"),
        type=item.get("type", ""),
        summary=item.get("summary"),
        url=item.get("url", ""),
        image_url=item.get("image_url"),
        collected_at=item.get("collected_at", ""),
        source_url=item.get("source_url", ""),
    ).clean()


def validate_offline() -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    html = SAMPLE_PAGE.read_text(encoding="utf-8")
    extracted_links = parse_park_links(html, SOURCE_URL, max_objects=MAX_OBJECTS)
    objects = load_jsonl(SAMPLE_OUTPUT)

    invalid_urls = [index for index, obj in enumerate(objects, 1) if not is_absolute_http_url(obj.get("url"))]
    invalid_images = [
        index for index, obj in enumerate(objects, 1)
        if obj.get("image_url") is not None and not is_absolute_http_url(obj.get("image_url"))
    ]
    invalid_provinces = [
        index for index, obj in enumerate(objects, 1)
        if not isinstance(obj.get("province"), str)
        or not obj["province"].strip()
        or obj["province"] != obj["province"].upper()
    ]
    if invalid_urls:
        errors.append(f"URLs de parc non absolues aux lignes : {invalid_urls}")
    if invalid_images:
        errors.append(f"URLs d'image non absolues aux lignes : {invalid_images}")
    if invalid_provinces:
        errors.append(f"Provinces non normalisées aux lignes : {invalid_provinces}")

    # Le lot de test contient le contenu exporté + un doublon + un objet incomplet.
    candidates = [as_place(item) for item in objects]
    if candidates:
        candidates.append(as_place(objects[0]))
    candidates.append(
        ProtectedPlace(
            id="fixture-incomplete",
            name=None,
            province="QC",
            type="National Park",
            summary="",
            url="https://parks.canada.ca/pn-np/qc/fixture-incomplete",
            image_url=None,
            collected_at="2026-07-31T07:00:00Z",
            source_url=SOURCE_URL,
        ).clean()
    )

    seen_ids: set[str] = set()
    exported = rejected = duplicates = missing_fields = 0
    for place in candidates:
        missing = place.missing_required_fields()
        if missing:
            rejected += 1
            missing_fields += len(missing)
            continue
        if place.id in seen_ids:
            rejected += 1
            duplicates += 1
            continue
        seen_ids.add(place.id)
        exported += 1

    if len(extracted_links) != len(objects):
        errors.append(
            f"La page locale fournit {len(extracted_links)} liens mais le JSONL contient {len(objects)} objets"
        )
    if duplicates != 1:
        errors.append(f"Le test attend 1 doublon rejeté, obtenu : {duplicates}")
    if missing_fields < 1:
        errors.append("L'objet incomplet n'a pas produit de champ manquant")
    if exported != len(objects):
        errors.append(f"Export attendu après tests : {len(objects)}, obtenu : {exported}")

    stats = {
        "Vus": len(candidates),
        "Exportés": exported,
        "Rejetés": rejected,
        "Doublons": duplicates,
        "Champs manquants": missing_fields,
    }
    return stats, errors


def print_table(stats: dict[str, int]) -> None:
    headers = list(stats.keys())
    widths = [max(len(header), len(str(stats[header]))) for header in headers]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(border)
    print("|" + "|".join(f" {header:<{width}} " for header, width in zip(headers, widths)) + "|")
    print(border)
    print("|" + "|".join(f" {stats[header]:<{width}} " for header, width in zip(headers, widths)) + "|")
    print(border)


def main() -> int:
    print("=== VÉRIFICATION HORS LIGNE — PARCS CANADA ===")
    for required in (SAMPLE_PAGE, SAMPLE_OUTPUT):
        if not required.exists():
            print(f"ECHEC : fichier introuvable : {required}")
            return 1

    try:
        stats, errors = validate_offline()
    except (OSError, ValueError, TypeError) as error:
        print(f"ECHEC : {error}")
        return 1

    print_table(stats)
    print("Normalisation URL absolue :", "OK" if not any("URL" in e for e in errors) else "ECHEC")
    print("Déduplication            :", "OK" if stats["Doublons"] == 1 else "ECHEC")
    print("Rejet champs manquants   :", "OK" if stats["Champs manquants"] >= 1 else "ECHEC")

    if errors:
        print("\nANOMALIES :")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nRésultat final : 3/3 contrôles réussis")
    return 0


if __name__ == "__main__":
    sys.exit(main())