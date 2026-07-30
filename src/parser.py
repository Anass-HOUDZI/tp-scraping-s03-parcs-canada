from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from .models import ProtectedPlace

def parse_places(html_content: str, source_url: str) -> list[ProtectedPlace]:
    """
    Analyse le HTML et extrait une liste d'objets ProtectedPlace.
    Sélecteurs ancrés sur la sémantique plutôt que sur le design.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    places = []
    
    # Horodatage standardisé en UTC
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # ⚠️ A AJUSTER : Ici on cible les cartes d'articles.
    # Tu devras ouvrir l'inspecteur web sur samples/sample_page.html
    # pour affiner ce sélecteur (ex: soup.find_all("li", class_="item-parc"))
    cards = soup.find_all("article") 
    
    for card in cards[:60]:  # Limite stricte imposée par la matrice S03
        try:
            # 1. Nom du parc (souvent dans un titre de niveau 3)
            title_tag = card.find("h3")
            name = title_tag.get_text(strip=True) if title_tag else "Nom inconnu"
            
            # 2. URL Absolue
            link_tag = card.find("a", href=True)
            raw_url = link_tag["href"] if link_tag else ""
            full_url = urljoin(source_url, raw_url)
            
            # 3. Résumé
            summary_tag = card.find("p")
            summary = summary_tag.get_text(strip=True) if summary_tag else "N/A"
            
            # 4. Image URL
            img_tag = card.find("img", src=True)
            img_url = urljoin(source_url, img_tag["src"]) if img_tag else None
            
            # 5. Type et Province (Valeurs par défaut à affiner selon le DOM de Parcs Canada)
            park_type = "Parc national"
            province = "CA" # Idéalement, à remonter depuis un conteneur parent (ex: section de province)
            
            # Génération d'un ID stable basé sur les données
            place_id = f"{province}-{name}".lower().replace(" ", "-").replace("'", "")
            
            # Instanciation du modèle
            place = ProtectedPlace(
                id=place_id,
                name=name,
                province=province,
                type=park_type,
                summary=summary,
                url=full_url,
                image_url=img_url,
                collected_at=now_iso,
                source_url=source_url
            )
            
            places.append(place)
            
        except Exception as e:
            print(f"⚠️ Élément ignoré suite à une erreur de parsing : {e}")
            continue
            
    print(f"🔍 Extraction terminée : {len(places)} lieux identifiés.")
    return places