from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, timezone

@dataclass
class ProtectedPlace:
    id: str                   # Identifiant unique généré (ex: qc-forillon)
    name: str                 # Nom du parc
    province: str             # Province (ex: Québec, Alberta)
    type: str                 # Type (Parc national, aire marine...)
    summary: str              # Courte description
    url: str                  # Lien absolu vers la fiche détail
    image_url: Optional[str]  # Lien de l'image (si présente)
    collected_at: str         # Horodatage ISO 8601
    source_url: str           # Page depuis laquelle la donnée a été extraite

    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'export JSONL."""
        return asdict(self)