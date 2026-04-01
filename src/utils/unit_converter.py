from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def parse_millimeters(
    raw_value: Any,
    field_name: str,
    row_number: int,
    logs: List[Dict[str, Any]],
) -> Optional[float]:
    if raw_value is None or str(raw_value).strip() == "":
        logs.append(
            {
                "level": "warning",
                "row": row_number,
                "field": field_name,
                "message": f"{field_name} is missing.",
            }
        )
        return None

    normalized = str(raw_value).strip().lower().replace(",", "")
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)(mm)?", normalized)
    if not match:
        logs.append(
            {
                "level": "warning",
                "row": row_number,
                "field": field_name,
                "message": f'{field_name} value "{raw_value}" is invalid.',
            }
        )
        return None

    return float(match.group(1))
