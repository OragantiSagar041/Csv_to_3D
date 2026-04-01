from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Position:
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Dimensions:
    width: float
    depth: float
    height: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "width": self.width,
            "depth": self.depth,
            "height": self.height,
        }


@dataclass
class RelativeReference:
    type: str
    entity_name: str
    source_row: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "entityName": self.entity_name,
            "sourceRow": self.source_row,
        }


@dataclass
class ModelEntity:
    entity_name: str
    level: int
    material: str
    dimensions: Dimensions
    position: Position
    source_row: int
    relative_to: Optional[RelativeReference] = None
    type: str = field(init=False, default="entity")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "entityName": self.entity_name,
            "level": self.level,
            "material": self.material,
            "dimensions": self.dimensions.to_dict(),
            "position": self.position.to_dict(),
            "relativeTo": self.relative_to.to_dict() if self.relative_to else None,
        }


@dataclass
class Wall(ModelEntity):
    type: str = field(init=False, default="wall")


@dataclass
class Cabinet(ModelEntity):
    planks: list["Plank"] = field(default_factory=list)
    type: str = field(init=False, default="cabinet")

    def add_plank(self, plank: "Plank") -> None:
        self.planks.append(plank)


@dataclass
class Plank(ModelEntity):
    plank_id: Optional[str] = None
    type: str = field(init=False, default="plank")

    def to_dict(self) -> Dict[str, Any]:
        payload = super().to_dict()
        payload["plankId"] = self.plank_id
        return payload
