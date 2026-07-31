from __future__ import annotations
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .models import ProtectedPlace


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(unescape(value).split())


def _stable_id(url: str) -> str:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return "-".join(parts[-3:]).lower()


def _province_from_url(url: str) -> str | None:
    parts = [part for part in urlparse(url).path.split("/") if part]
    try:
        index = parts.index("pn-np")
    except ValueError:
        return None
    return parts[index + 1].upper() if index + 1 < len(parts) else ""


def _type_from_name(name: str | None) -> str:
    lowered = (name or "").lower()
    if "national park and reserve" in lowered:
        return "National Park and Reserve"
    if "national park reserve" in lowered:
        return "National Park Reserve"
    if "national park" in lowered or "parc national" in lowered:
        return "National Park"
    return "Protected Place"


def parse_park_links(
    html_content: str,
    source_url: str,
    max_objects: int = 60,
    logger=None,
) -> list[dict[str, str]]:
    """Extrait les liens de parcs à partir d'ancres sémantiques et les déduplique."""
    soup = BeautifulSoup(html_content, "html.parser")
    results: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    # Une ancre avec href est plus stable qu'une classe CSS générée.
    for anchor in soup.find_all("a", href=True):
        name = _clean_text(anchor.get_text(" ", strip=True))
        absolute_url = urljoin(source_url, anchor.get("href", ""))
        parsed = urlparse(absolute_url)
        path = parsed.path.rstrip("/")

        name_matches = "national park" in name.lower() or "parc national" in name.lower()
        path_matches = path.startswith("/pn-np/")
        enough_segments = len([part for part in path.split("/") if part]) >= 3

        if not (name_matches and path_matches and enough_segments):
            continue
        if absolute_url in seen_urls:
            if logger:
                logger.warning("Lien dupliqué ignoré : %s", absolute_url)
            continue

        seen_urls.add(absolute_url)
        results.append({"name": name, "url": absolute_url})
        if len(results) >= max_objects:
            break

    if logger and not results:
        logger.warning("Aucun lien de parc trouvé : vérifier la structure HTML")
    return results


def _extract_name(soup: BeautifulSoup, fallback_name: str, logger=None) -> str | None:
    """Extrait le nom via h1, puis métadonnée Open Graph, puis repli de liste."""
    h1 = soup.find("h1")
    og_title = soup.find("meta", attrs={"property": "og:title"})
    sources_found = h1 is not None or og_title is not None or bool(fallback_name)

    candidates = [
        h1.get_text(" ", strip=True) if h1 else "",
        og_title.get("content", "") if og_title else "",
        fallback_name,
    ]
    for raw in candidates:
        name = _clean_text(raw).replace(" - Parks Canada", "").strip()
        if name:
            return name

    if logger:
        logger.warning("Nom introuvable dans h1, og:title et fallback")
    return "" if sources_found else None


def _extract_summary(soup: BeautifulSoup, logger=None) -> str | None:
    """Extrait un résumé via le contenu principal, puis les métadonnées."""
    h1 = soup.find("h1")
    source_found = False

    if h1:
        main = soup.find("main")
        paragraphs = main.find_all("p") if main else h1.find_all_next("p")
        for paragraph in paragraphs:
            source_found = True
            candidate = _clean_text(paragraph.get_text(" ", strip=True))
            if len(candidate) >= 40:
                return candidate

    for attrs in ({"property": "og:description"}, {"name": "description"}):
        tag = soup.find("meta", attrs=attrs)
        if tag is not None:
            source_found = True
            candidate = _clean_text(tag.get("content", ""))
            if candidate:
                return candidate

    if logger:
        logger.warning("Résumé introuvable dans le contenu principal et les métadonnées")
    return "" if source_found else None


def _extract_image_url(soup: BeautifulSoup, page_url: str, logger=None) -> str | None:
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        return urljoin(page_url, og_image.get("content"))

    main = soup.find("main")
    image = main.find("img", src=True) if main else None
    if image:
        return urljoin(page_url, image.get("src"))

    if logger:
        logger.warning("Image absente pour %s (champ optionnel)", page_url)
    return None


def parse_park_detail(
    html_content: str,
    page_url: str,
    source_url: str,
    fallback_name: str = "",
    logger=None,
) -> ProtectedPlace:
    """Construit un ``ProtectedPlace`` sans faire échouer le lot si un champ manque."""
    soup = BeautifulSoup(html_content, "html.parser")
    place = ProtectedPlace(
        id=_stable_id(page_url),
        name=_extract_name(soup, fallback_name, logger),
        province=_province_from_url(page_url),
        type="",
        summary=_extract_summary(soup, logger),
        url=urljoin(source_url, page_url),
        image_url=_extract_image_url(soup, page_url, logger),
        collected_at=datetime.now(timezone.utc).isoformat(),
        source_url=source_url,
    )
    place.type = _type_from_name(place.name)
    return place.clean()
