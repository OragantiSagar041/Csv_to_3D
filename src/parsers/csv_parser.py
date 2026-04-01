from __future__ import annotations

import csv
import io
from typing import Dict, List

from src.utils.normalizers import normalize_header


def parse_csv(text: str) -> List[Dict[str, str]]:
    if not text.strip():
        return []

    reader = csv.DictReader(io.StringIO(text))
    rows: List[Dict[str, str]] = []

    for index, raw_row in enumerate(reader, start=2):
        row: Dict[str, str] = {"__rowNumber": index}
        for header, value in raw_row.items():
            clean_header = (header or "").strip()
            clean_value = (value or "").strip()
            row[clean_header] = clean_value
            row[normalize_header(clean_header)] = clean_value
        rows.append(row)

    return rows
