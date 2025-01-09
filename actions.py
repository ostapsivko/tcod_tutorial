from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class Action: 
    def perform(self, engine:Engine, entity:Entity) -> None:
        """Perform this aciton with the objects needed to determine its scope
        `engine` is the scope this aciton is being performed in
        `entity` is the object performing the action

        This method must be overriden by Action subclasses
        """

        raise NotImplementedError

class ActionWithDirection(Action):
    def __init__(self, dx:int, dy:int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, engine:Engine, entity:Entity):
        raise NotImplementedError

class EscapeAction(Action):
    def perform(self, engine, entity) -> None:
        raise SystemExit

class MovementAction(ActionWithDirection):

    def perform(self, engine:Engine, entity:Entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if not engine.map.in_bounds(dest_x, dest_y):
            return # Destination is out of bounds.
        if not engine.map.tiles["walkable"][dest_x, dest_y]:
            return # Destination is blocked by a tile.
        if engine.map.get_blocking_entity_at(dest_x, dest_y):
            return # Destination is blocked by another entity

        entity.move(self.dx, self.dy)

class MeleeAction(ActionWithDirection):
    def perform(self, engine:Engine, entity:Entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        target = engine.map.get_blocking_entity_at(dest_x, dest_y)

        if not target:
            return # Nobody to attack
        
        print(f"You kick the {target.name}, much to its annoyance!")

class BumpAction(ActionWithDirection):

    def perform(self, engine, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if engine.map.get_blocking_entity_at(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        
        else:
            return MovementAction(self.dx, self.dy).perform(engine, entity)
