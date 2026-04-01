from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from src.models.entities import Cabinet, Dimensions, Plank, Position, RelativeReference, Wall
from src.utils.normalizers import get_field
from src.utils.unit_converter import parse_millimeters


def parse_integer(raw_value: str) -> Optional[int]:
    if raw_value is None or str(raw_value).strip() == "":
        return None

    try:
        return int(str(raw_value).strip())
    except ValueError:
        return None


def parse_dimensions(row: Dict[str, str], row_number: int, logs: List[Dict[str, Any]]) -> Dimensions:
    return Dimensions(
        width=parse_millimeters(get_field(row, ["LenX", "LengthX", "Width"]), "LenX", row_number, logs),
        depth=parse_millimeters(get_field(row, ["LenY", "LengthY", "Depth"]), "LenY", row_number, logs),
        height=parse_millimeters(get_field(row, ["LenZ", "LengthZ", "Height"]), "LenZ", row_number, logs),
    )


def parse_position(row: Dict[str, str], row_number: int, logs: List[Dict[str, Any]]) -> Position:
    return Position(
        x=parse_millimeters(get_field(row, ["X", "PosX", "PositionX"]), "X", row_number, logs),
        y=parse_millimeters(get_field(row, ["Y", "PosY", "PositionY"]), "Y", row_number, logs),
        z=parse_millimeters(get_field(row, ["Z", "PosZ", "PositionZ"]), "Z", row_number, logs),
    )


def has_valid_dimensions(dimensions: Dimensions) -> bool:
    return all(value is not None and value > 0 for value in asdict(dimensions).values())


def has_valid_position(position: Position) -> bool:
    return all(value is not None for value in asdict(position).values())


def create_entity(row: Dict[str, str], logs: List[Dict[str, Any]]):
    row_number = row["__rowNumber"]
    entity_name = get_field(row, ["Entity Name", "EntityName", "Name", "ObjectName"]) or f"Row {row_number}"
    material = get_field(row, ["Material"]) or "unknown"
    level = parse_integer(get_field(row, ["Level"]))
    plank_id = get_field(row, ["plank_id", "Plank ID", "PlankId"]) or None

    if level not in {0, 1, 2}:
        logs.append(
            {
                "level": "warning",
                "row": row_number,
                "message": f'Invalid level for "{entity_name}". Row skipped.',
            }
        )
        return None

    dimensions = parse_dimensions(row, row_number, logs)
    position = parse_position(row, row_number, logs)

    if not has_valid_dimensions(dimensions):
        logs.append(
            {
                "level": "warning",
                "row": row_number,
                "message": f'Non-positive or invalid dimensions for "{entity_name}". Row skipped.',
            }
        )
        return None

    if not has_valid_position(position):
        logs.append(
            {
                "level": "warning",
                "row": row_number,
                "message": f'Invalid position for "{entity_name}". Row skipped.',
            }
        )
        return None

    common_kwargs = {
        "entity_name": entity_name,
        "level": level,
        "material": material,
        "dimensions": dimensions,
        "position": position,
        "source_row": row_number,
    }

    if level == 0:
        return Wall(**common_kwargs)
    if level == 1:
        return Cabinet(**common_kwargs)
    return Plank(**common_kwargs, plank_id=plank_id)


def create_material_groups(cabinets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for entry in cabinets:
        entities = [entry["cabinet"], *entry["planks"]]
        for entity in entities:
            groups.setdefault(entity.material, []).append(
                {
                    "type": entity.type,
                    "entityName": entity.entity_name,
                    "sourceRow": entity.source_row,
                }
            )

    return groups


def build_model(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    logs: List[Dict[str, Any]] = []
    wall: Optional[Wall] = None
    current_cabinet: Optional[Cabinet] = None
    cabinets: List[Dict[str, Any]] = []

    for row in rows:
        entity = create_entity(row, logs)
        if entity is None:
            continue

        if isinstance(entity, Wall):
            if wall is not None:
                logs.append(
                    {
                        "level": "warning",
                        "row": row["__rowNumber"],
                        "message": f'Additional wall "{entity.entity_name}" ignored because one wall is already assigned.',
                    }
                )
                continue

            wall = entity
            current_cabinet = None
            continue

        if isinstance(entity, Cabinet):
            if wall is None:
                logs.append(
                    {
                        "level": "warning",
                        "row": row["__rowNumber"],
                        "message": f'Cabinet "{entity.entity_name}" has no wall parent. Row skipped.',
                    }
                )
                continue

            entity.relative_to = RelativeReference("wall", wall.entity_name, wall.source_row)
            current_cabinet = entity
            cabinets.append({"cabinet": entity, "planks": []})
            continue

        if current_cabinet is None:
            logs.append(
                {
                    "level": "warning",
                    "row": row["__rowNumber"],
                    "message": f'Plank "{entity.entity_name}" has no cabinet parent. Row skipped.',
                }
            )
            continue

        entity.relative_to = RelativeReference("cabinet", current_cabinet.entity_name, current_cabinet.source_row)
        current_cabinet.add_plank(entity)
        cabinets[-1]["planks"].append(entity)

    if wall is None:
        logs.append({"level": "error", "row": None, "message": "No valid wall row found."})

    return {
        "wall": wall.to_dict() if wall else None,
        "cabinets": [
            {
                "cabinet": entry["cabinet"].to_dict(),
                "planks": [plank.to_dict() for plank in entry["planks"]],
            }
            for entry in cabinets
        ],
        "metadata": {
            "cabinetCount": len(cabinets),
            "plankCount": sum(len(entry["planks"]) for entry in cabinets),
            "materialGroups": create_material_groups(cabinets),
            "validationLogs": logs,
        },
    }
