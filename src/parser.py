from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .models import ProtectedPlace


def _clean_text(value: str | None) -> str:
    """
    Nettoie les espaces et les entités HTML.
    """

    if not value:
        return ""

    return " ".join(
        unescape(value).split()
    )


def _stable_id(url: str) -> str:
    """
    Génère un identifiant stable à partir de l'URL.
    """

    path_parts = [
        part
        for part in urlparse(url).path.split("/")
        if part
    ]

    if len(path_parts) >= 3:
        useful_parts = path_parts[-3:]
    else:
        useful_parts = path_parts

    return "-".join(useful_parts).lower()


def _province_from_url(url: str) -> str:
    """
    Extrait le code de province depuis l'URL.
    """

    parts = [
        part
        for part in urlparse(url).path.split("/")
        if part
    ]

    try:
        index = parts.index("pn-np")
        return parts[index + 1].upper()

    except (ValueError, IndexError):
        return ""


def _type_from_name(name: str) -> str:
    """
    Déduit le type du lieu depuis son nom.
    """

    lowered = name.lower()

    if "national park and reserve" in lowered:
        return "National Park and Reserve"

    if "national park reserve" in lowered:
        return "National Park Reserve"

    if "national park" in lowered:
        return "National Park"

    return "Protected Place"


def parse_park_links(
    html_content: str,
    source_url: str,
    max_objects: int = 60,
) -> list[dict[str, str]]:
    """
    Extrait et déduplique les liens des parcs
    depuis la page contenant la liste.
    """

    soup = BeautifulSoup(
        html_content,
        "html.parser",
    )

    results = []
    seen_urls = set()

    for anchor in soup.find_all(
        "a",
        href=True,
    ):
        name = _clean_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        absolute_url = urljoin(
            source_url,
            anchor.get("href", ""),
        )

        path = urlparse(
            absolute_url
        ).path.rstrip("/")

        if "national park" not in name.lower():
            continue

        if not path.startswith("/pn-np/"):
            continue

        parts = [
            part
            for part in path.split("/")
            if part
        ]

        if len(parts) < 3:
            continue

        if absolute_url in seen_urls:
            continue

        seen_urls.add(absolute_url)

        results.append(
            {
                "name": name,
                "url": absolute_url,
            }
        )

        if len(results) >= max_objects:
            break

    return results


def parse_park_detail(
    html_content: str,
    page_url: str,
    source_url: str,
    fallback_name: str = "",
) -> ProtectedPlace:
    """
    Extrait les informations d'une page détail.
    """

    soup = BeautifulSoup(
        html_content,
        "html.parser",
    )

    # Nom
    h1 = soup.find("h1")

    name = _clean_text(
        h1.get_text(
            " ",
            strip=True,
        )
        if h1
        else ""
    )

    # Solution de secours avec og:title
    if not name:
        og_title = soup.find(
            "meta",
            attrs={
                "property": "og:title"
            },
        )

        name = _clean_text(
            og_title.get("content")
            if og_title
            else ""
        )

    # Nom provenant de la page liste
    if not name:
        name = _clean_text(
            fallback_name
        )

    name = name.replace(
        " - Parks Canada",
        "",
    ).strip()

    # Résumé
    summary = ""

    if h1:
        for paragraph in h1.find_all_next("p"):
            candidate = _clean_text(
                paragraph.get_text(
                    " ",
                    strip=True,
                )
            )

            if len(candidate) >= 40:
                summary = candidate
                break

    # Solution de secours avec les métadonnées
    if not summary:
        metadata_options = (
            {
                "property": "og:description"
            },
            {
                "name": "description"
            },
        )

        for attrs in metadata_options:
            tag = soup.find(
                "meta",
                attrs=attrs,
            )

            candidate = _clean_text(
                tag.get("content")
                if tag
                else ""
            )

            if candidate:
                summary = candidate
                break

    # Image
    image_url = None

    og_image = soup.find(
        "meta",
        attrs={
            "property": "og:image"
        },
    )

    if (
        og_image
        and og_image.get("content")
    ):
        image_url = urljoin(
            page_url,
            og_image.get("content"),
        )

    # Image de secours dans main
    if not image_url:
        main_content = soup.find("main")

        image = (
            main_content.find(
                "img",
                src=True,
            )
            if main_content
            else None
        )

        if image:
            image_url = urljoin(
                page_url,
                image.get("src"),
            )

    return ProtectedPlace(
        id=_stable_id(page_url),
        name=name,
        province=_province_from_url(
            page_url
        ),
        type=_type_from_name(name),
        summary=summary,
        url=page_url,
        image_url=image_url,
        collected_at=datetime.now(
            timezone.utc
        ).isoformat(),
        source_url=source_url,
    )


def parse_places(
    html_content: str,
    source_url: str,
) -> list[ProtectedPlace]:
    """
    Fonction utilisée pour la vérification hors ligne.
    """

    soup = BeautifulSoup(
        html_content,
        "html.parser",
    )

    places = []

    cards = soup.select(
        "article[data-park-card], "
        "article.park-card"
    )

    for card in cards[:60]:
        link = card.find(
            "a",
            href=True,
        )

        if not link:
            continue

        page_url = urljoin(
            source_url,
            link.get("href", ""),
        )

        name_tag = card.find(
            [
                "h2",
                "h3",
                "h4",
            ]
        )

        name = _clean_text(
            name_tag.get_text(
                " ",
                strip=True,
            )
            if name_tag
            else ""
        )

        summary_tag = card.find("p")

        summary = _clean_text(
            summary_tag.get_text(
                " ",
                strip=True,
            )
            if summary_tag
            else ""
        )

        image = card.find(
            "img",
            src=True,
        )

        province = (
            card.get(
                "data-province",
                "",
            )
            or _province_from_url(
                page_url
            )
        )

        park_type = (
            card.get(
                "data-type",
                "",
            )
            or _type_from_name(name)
        )

        place = ProtectedPlace(
            id=_stable_id(page_url),
            name=name,
            province=province,
            type=park_type,
            summary=summary,
            url=page_url,
            image_url=(
                urljoin(
                    source_url,
                    image.get("src"),
                )
                if image
                else None
            ),
            collected_at=datetime.now(
                timezone.utc
            ).isoformat(),
            source_url=source_url,
        )

        places.append(place)

    return places