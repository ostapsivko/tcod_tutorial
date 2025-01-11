from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from components.consumable import Consumable
    from components.inventory import Inventory
    from game_map import GameMap

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent player, enemy, item etc.
    """
    parent: Union[GameMap,Inventory]

    def __init__(
            self,
            map:Optional[GameMap] = None, 
            x:int = 0, 
            y:int = 0, 
            char:str = "?", 
            color:Tuple[int, int, int] = (255, 255, 255),
            name:str = "<Unnamed>",
            blocks_movement:bool = False,
            render_order:RenderOrder = RenderOrder.CORPSE,
            ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order

        if map:
            self.parent = map
            map.entities.add(self)


    @property
    def map(self) -> GameMap:
        return self.parent.map

    def move(self, dx:int, dy:int) -> None:
        self.x += dx
        self.y += dy


    def spawn(self: T, gamemap:GameMap, x:int, y:int) -> T:
        """Spawn a copy of this instance at a given location"""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone
    
    def place(self, x:int, y:int, map:Optional[GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across game map"""
        self.x = x
        self.y = y
        if map:
            if hasattr(self, "parent"):
                if self.parent is self.map:
                    self.map.entities.remove(self)
            self.parent = map
            map.entities.add(self)

    def distance(self, x:int, y:int) -> float:
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

class Actor(Entity):
    def __init__(
            self, 
            *,
            x = 0, 
            y = 0, 
            char:str = "?", 
            color = (255, 255, 255), 
            name = "<Unnamed>", 
            ai_cls: Type[BaseAI],
            fighter: Fighter,
            inventory:Inventory,
            ):
        super().__init__(x=x, y=y, char=char, color=color, name=name, blocks_movement=True, render_order=RenderOrder.ACTOR)

        self.ai:Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.parent = self
    
        self.inventory = inventory
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions"""
        return bool(self.ai)
    
class Item(Entity):
    def __init__(
            self,
            *, 
            x = 0, 
            y = 0, 
            char = "?", 
            color = (255, 255, 255), 
            name = "<Unnamed>", 
            consumable:Consumable):
        super().__init__(x=x, 
                         y=y, 
                         char=char, 
                         color=color, 
                         name=name, 
                         blocks_movement=False, 
                         render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable
        self.consumable.parent = self