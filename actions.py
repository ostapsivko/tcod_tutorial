from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

import color
from entity import Actor
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity, Actor, Item

class Action: 
    def __init__(self, entity:Actor):
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

        raise NotImplementedError()

class ActionWithDirection(Action):
    def __init__(self, entity:Actor, dx:int, dy:int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int,int]:
        """Returns this actions destination"""
        return self.entity.x + self.dx, self.entity.y + self.dy
    
    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination"""
        return self.engine.map.get_blocking_entity_at(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination"""
        return self.engine.map.get_actor_at(*self.dest_xy)

    def perform(self):
        raise NotImplementedError()

class MovementAction(ActionWithDirection):

    def perform(self):
        dest_x, dest_y = self.dest_xy

        if not self.engine.map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.map.get_blocking_entity_at(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)

class MeleeAction(ActionWithDirection):
    def perform(self):
        target = self.target_actor

        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(f"{attack_desc} for {damage} hit points", fg=attack_color)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(f"{attack_desc} but does no damage", attack_color)

class BumpAction(ActionWithDirection):

    def perform(self):
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

class WaitAction(Action):
    def perform(self):
        pass

class ItemAction(Action):
    def __init__(
            self, entity:Actor, item:Item, target_xy: Optional[Tuple[int,int]] = None
            ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        return self.engine.map.get_actor_at(*self.target_xy)
    
    def perform(self):
        self.item.consumable.activate(self)

class PickupAction(Action):
    def __init__(self, entity):
        super().__init__(entity)

    def perform(self):
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")
                
                self.engine.map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}")
                return
            
        raise exceptions.Impossible("There is nothing here to pick up.")
    
class DropAction(ItemAction):
    def perform(self):
        self.entity.inventory.drop(self.item)