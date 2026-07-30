from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class ProtectedPlace:
    """
    Contrat de données attendu pour la cible S03 Parcs Canada.
    """

    id: str
    name: str
    province: str
    type: str
    summary: str
    url: str
    image_url: Optional[str]
    collected_at: str
    source_url: str

    def to_dict(self) -> dict:
        return asdict(self)

    def missing_required_fields(self) -> list[str]:
        """
        Retourne les champs obligatoires absents ou vides.
        """
        required = {
            "id": self.id,
            "name": self.name,
            "province": self.province,
            "type": self.type,
            "summary": self.summary,
            "url": self.url,
            "collected_at": self.collected_at,
            "source_url": self.source_url,
        }

        return [
            field
            for field, value in required.items()
            if value is None
            or (
                isinstance(value, str)
                and not value.strip()
            )
        ]

    def is_valid(self) -> bool:
        return not self.missing_required_fields()