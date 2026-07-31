"""Modèle métier et normalisation des lieux protégés."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

_EMPTY_MARKERS = {"n/a", "na", "non disponible", "not available", "-", "—"}


@dataclass
class ProtectedPlace:
    """Représente un parc ou un lieu protégé extrait de Parcs Canada."""

    id: str
    name: Optional[str]
    province: Optional[str]
    type: str
    summary: Optional[str]
    url: str
    image_url: Optional[str]
    collected_at: str
    source_url: str

    REQUIRED_FIELDS = (
        "id",
        "name",
        "province",
        "type",
        "summary",
        "url",
        "collected_at",
        "source_url",
    )

    @staticmethod
    def _clean_optional_text(value: Optional[str]) -> Optional[str]:
        """Nettoie une chaîne et convertit les marqueurs N/A en ``None``."""
        if value is None:
            return None
        cleaned = " ".join(str(value).split())
        if cleaned.lower() in _EMPTY_MARKERS:
            return None
        return cleaned

    @staticmethod
    def _normalize_utc(value: str | datetime | None) -> str:
        """Retourne un horodatage ISO 8601 en UTC avec suffixe ``Z``."""
        if value is None or value == "":
            dt = datetime.now(timezone.utc)
        elif isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def clean(self) -> "ProtectedPlace":
        """Normalise l'objet en place puis le retourne pour permettre le chaînage."""
        self.id = (self._clean_optional_text(self.id) or "").lower()
        self.name = self._clean_optional_text(self.name)
        self.province = self._clean_optional_text(self.province)
        if self.province is not None:
            self.province = self.province.upper()
        self.type = self._clean_optional_text(self.type) or "Protected Place"
        self.summary = self._clean_optional_text(self.summary)
        self.url = self._clean_optional_text(self.url) or ""
        self.image_url = self._clean_optional_text(self.image_url)
        self.source_url = self._clean_optional_text(self.source_url) or ""
        self.collected_at = self._normalize_utc(self.collected_at)
        return self

    def to_dict(self) -> dict:
        """Sérialise l'objet après normalisation."""
        self.clean()
        return asdict(self)

    def field_status(self) -> dict[str, str]:
        """Distingue les champs corrects, absents (None) et vides ("")."""
        status: dict[str, str] = {}
        for field_name in self.REQUIRED_FIELDS:
            value = getattr(self, field_name)
            if value is None:
                status[field_name] = "absent"
            elif isinstance(value, str) and not value.strip():
                status[field_name] = "vide"
            else:
                status[field_name] = "ok"
        return status

    def missing_required_fields(self) -> list[str]:
        return [name for name, state in self.field_status().items() if state != "ok"]

    def is_valid(self) -> bool:
        return not self.missing_required_fields()
