from __future__ import annotations

from config import (
    ACCEPT_LANGUAGE,
    BACKOFF_FACTOR,
    LIST_URL,
    LOG_FILE,
    MAX_OBJECTS,
    MAX_RETRIES,
    OUTPUT_JSONL,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    SAMPLE_JSONL,
    SOURCE_URL,
    USER_AGENT,
)
from src.exporter import export_to_jsonl
from src.fetcher import Fetcher
from src.logger import get_logger
from src.parser import parse_park_detail, parse_park_links


def main() -> int:
    logger = get_logger(log_file=LOG_FILE)
    valid_places = []
    seen_ids: set[str] = set()
    rejected_count = duplicate_count = missing_fields_count = 0

    with Fetcher(
        user_agent=USER_AGENT,
        accept_language=ACCEPT_LANGUAGE,
        delay=REQUEST_DELAY,
        timeout=REQUEST_TIMEOUT,
        max_retries=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        logger=logger,
    ) as fetcher:
        logger.info("Début du scraping | cible=%s | plafond=%s", LIST_URL, MAX_OBJECTS)
        listing_html = fetcher.fetch_page(LIST_URL)
        if listing_html is None:
            logger.error("Impossible de télécharger la page de liste")
            return 1

        park_links = parse_park_links(
            listing_html,
            source_url=LIST_URL,
            max_objects=MAX_OBJECTS,
            logger=logger,
        )

        for index, link in enumerate(park_links, start=1):
            logger.info("Traitement %s/%s : %s", index, len(park_links), link["url"])
            detail_html = fetcher.fetch_page(link["url"])
            if detail_html is None:
                rejected_count += 1
                logger.warning("Objet rejeté : page non téléchargée | %s", link["url"])
                continue

            place = parse_park_detail(
                detail_html,
                page_url=link["url"],
                source_url=SOURCE_URL,
                fallback_name=link["name"],
                logger=logger,
            )
            missing = place.missing_required_fields()
            if missing:
                rejected_count += 1
                missing_fields_count += len(missing)
                logger.warning("Objet rejeté | id=%s | champs=%s", place.id, ", ".join(missing))
                continue

            if place.id in seen_ids:
                rejected_count += 1
                duplicate_count += 1
                logger.warning("Doublon rejeté | id=%s", place.id)
                continue

            seen_ids.add(place.id)
            valid_places.append(place)

    exported = export_to_jsonl(valid_places, OUTPUT_JSONL) if valid_places else 0
    if valid_places:
        export_to_jsonl(valid_places, SAMPLE_JSONL)

    print("\nRÉCAPITULATIF")
    print(f"Vus             : {len(park_links)}")
    print(f"Exportés        : {exported}")
    print(f"Rejetés         : {rejected_count}")
    print(f"Doublons        : {duplicate_count}")
    print(f"Champs manquants: {missing_fields_count}")
    logger.info(
        "Fin | vus=%s exportés=%s rejetés=%s doublons=%s champs_manquants=%s",
        len(park_links), exported, rejected_count, duplicate_count, missing_fields_count,
    )
    return 0 if exported else 1


if __name__ == "__main__":
    raise SystemExit(main())