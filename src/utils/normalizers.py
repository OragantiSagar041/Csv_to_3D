from __future__ import annotations

from typing import Iterable, Mapping


def normalize_header(header: str) -> str:
    return "".join(character for character in str(header).strip().lower() if character.isalnum())


def get_field(row: Mapping[str, str], candidates: Iterable[str]) -> str:
    for candidate in candidates:
        if row.get(candidate, "") != "":
            return row[candidate]

        normalized_candidate = normalize_header(candidate)
        if row.get(normalized_candidate, "") != "":
            return row[normalized_candidate]

    return ""
