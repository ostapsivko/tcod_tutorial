from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from game_map import GameMap

class BaseComponent:
    parent:Entity

    @property
    def map(self) -> GameMap:
        return self.parent.map

    @property
    def engine(self) -> Engine:
        return self.map.engine