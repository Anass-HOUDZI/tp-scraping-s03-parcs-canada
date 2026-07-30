from config import (
    ACCEPT_LANGUAGE,
    LIST_URL,
    LOG_FILE,
    MAX_OBJECTS,
    OUTPUT_JSONL,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    SOURCE_URL,
    USER_AGENT,
)

from src.exporter import export_to_jsonl
from src.fetcher import Fetcher
from src.logger import get_logger
from src.parser import (
    parse_park_detail,
    parse_park_links,
)


def main():
    """
    Lance le scraping des parcs nationaux du Canada.
    """

    logger = get_logger(
        name="parcs_canada",
        log_file=LOG_FILE,
    )

    fetcher = Fetcher(
        user_agent=USER_AGENT,
        accept_language=ACCEPT_LANGUAGE,
        delay=REQUEST_DELAY,
        timeout=REQUEST_TIMEOUT,
        logger=logger,
    )

    valid_places = []
    seen_ids = set()

    rejected_count = 0
    duplicate_count = 0
    missing_fields_count = 0

    try:
        logger.info(
            "Début du scraping des parcs du Canada"
        )

        # Télécharger la page contenant la liste des parcs
        listing_html = fetcher.fetch_page(
            LIST_URL
        )

        if not listing_html:
            logger.error(
                "Impossible de télécharger la page "
                "contenant la liste des parcs."
            )

            print(
                "Impossible de télécharger la page "
                "contenant la liste des parcs."
            )

            return

        # Extraire les liens des parcs
        park_links = parse_park_links(
            html_content=listing_html,
            source_url=LIST_URL,
            max_objects=MAX_OBJECTS,
        )

        print(
            f"Nombre de parcs trouvés : "
            f"{len(park_links)}"
        )

        # Parcourir chaque parc
        for index, park_link in enumerate(
            park_links,
            start=1,
        ):
            park_name = park_link["name"]
            park_url = park_link["url"]

            print(
                f"[{index}/{len(park_links)}] "
                f"{park_name}"
            )

            # Télécharger la page de détail
            detail_html = fetcher.fetch_page(
                park_url
            )

            if not detail_html:
                rejected_count += 1

                logger.warning(
                    "Page non téléchargée : %s",
                    park_name,
                )

                print(
                    f"Page non téléchargée : "
                    f"{park_name}"
                )

                continue

            # Extraire les informations détaillées
            place = parse_park_detail(
                html_content=detail_html,
                page_url=park_url,
                source_url=SOURCE_URL,
                fallback_name=park_name,
            )

            # Vérifier les champs obligatoires
            missing_fields = (
                place.missing_required_fields()
            )

            if missing_fields:
                rejected_count += 1
                missing_fields_count += len(
                    missing_fields
                )

                logger.warning(
                    "Objet rejeté : %s | "
                    "Champs manquants : %s",
                    park_name,
                    ", ".join(missing_fields),
                )

                print(
                    f"Objet rejeté : {park_name}"
                )

                print(
                    "Champs manquants :",
                    ", ".join(missing_fields),
                )

                continue

            # Vérifier les doublons
            if place.id in seen_ids:
                rejected_count += 1
                duplicate_count += 1

                logger.warning(
                    "Doublon ignoré : %s",
                    place.id,
                )

                print(
                    f"Doublon ignoré : {place.id}"
                )

                continue

            seen_ids.add(place.id)
            valid_places.append(place)

        print("\nScraping terminé")

        print(
            "Nombre de parcs trouvés :",
            len(park_links),
        )

        print(
            "Nombre de parcs valides :",
            len(valid_places),
        )

        print(
            "Nombre de parcs rejetés :",
            rejected_count,
        )

        print(
            "Nombre de doublons :",
            duplicate_count,
        )

        print(
            "Nombre de champs manquants :",
            missing_fields_count,
        )

        # Exporter tous les parcs valides
        # dans samples/sample_output.jsonl
        if valid_places:
            export_to_jsonl(
                valid_places,
                OUTPUT_JSONL,
            )

            print(
                f"{len(valid_places)} parcs exportés "
                f"dans {OUTPUT_JSONL}"
            )

            logger.info(
                "%s parcs exportés dans %s",
                len(valid_places),
                OUTPUT_JSONL,
            )
        else:
            print(
                "Aucune donnée valide à exporter."
            )

            logger.warning(
                "Aucune donnée valide à exporter."
            )

    except Exception as error:
        logger.exception(
            "Une erreur inattendue est survenue : %s",
            error,
        )

        print(
            "Une erreur inattendue est survenue :",
            error,
        )

    finally:
        fetcher.close()
        logger.info("Fin du programme")


if __name__ == "__main__":
    main()