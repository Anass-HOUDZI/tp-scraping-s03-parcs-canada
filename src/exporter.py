from __future__ import annotations

import json
from pathlib import Path

from .models import ProtectedPlace


def export_to_jsonl(places: list[ProtectedPlace], output_path: str) -> int:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as file:
        for place in places:
            file.write(json.dumps(place.to_dict(), ensure_ascii=False, sort_keys=True))
            file.write("\n")

    return len(places)