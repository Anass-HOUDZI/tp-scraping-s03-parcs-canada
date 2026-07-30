import time
import requests
from typing import Optional

def fetch_page(url: str, delay: float = 1.5) -> Optional[str]:
    """
    Télécharge le contenu HTML d'une URL de manière éthique et robuste.
    Intègre une pause obligatoire pour ne pas surcharger le serveur.
    """
    print(f"⏳ Attente de {delay}s par courtoisie (respect éthique)...")
    time.sleep(delay)
    
    # En-têtes vitaux : Identification claire + Forçage du Français (Spécificité S03)
    headers = {
        "User-Agent": "TP-Scraping-Student/1.0 (Contact: anass.houdzi@efficom.fr)",
        "Accept-Language": "fr-CA,fr;q=0.9,en;q=0.8"
    }
    
    try:
        print(f"🌐 Téléchargement de : {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        # Lève une exception si le statut HTTP est une erreur (404, 500, etc.)
        response.raise_for_status()
        
        print("✅ Page téléchargée avec succès.")
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau lors de l'accès à {url} : {e}")
        return None