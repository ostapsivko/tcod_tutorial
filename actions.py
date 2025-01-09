from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class Action: 
    def __init__(self, entity:Entity):
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to"""
        return self.entity.map.engine

    def perform(self) -> None:
        """Perform this aciton with the objects needed to determine its scope
        `self.engine` is the scope this aciton is being performed in
        `self.entity` is the object performing the action

        This method must be overriden by Action subclasses
        """

        raise NotImplementedError

class ActionWithDirection(Action):
    def __init__(self, entity:Entity, dx:int, dy:int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    def perform(self):
        raise NotImplementedError

    @property
    def dest_xy(self) -> Tuple[int,int]:
        """Returns this actions destination"""
        return self.entity.x + self.dx, self.entity.y + self.dy
    
    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination"""
        return self.engine.map.get_blocking_entity_at(*self.dest_xy)

class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit

class MovementAction(ActionWithDirection):

    def perform(self):
        dest_x, dest_y = self.dest_xy

        if not self.engine.map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not self.engine.map.tiles["walkable"][dest_x, dest_y]:
            return # Destination is blocked by a tile.
        if self.engine.map.get_blocking_entity_at(dest_x, dest_y):
            return # Destination is blocked by another entity

        self.entity.move(self.dx, self.dy)

class MeleeAction(ActionWithDirection):
    def perform(self):
        target = self.blocking_entity

        if not target:
            return # Nobody to attack
        
        print(f"You kick the {target.name}, much to its annoyance!")

class BumpAction(ActionWithDirection):

    def perform(self):
        if self.blocking_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

class WaitAction(Action):
    def perform(self):
        pass