from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple

import numpy as np # type:ignore
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action, BaseComponent):
    entity:Actor

    def perform(self):
        raise NotImplementedError
    
    def get_path_to(self, dest_x, dest_y) -> List[Tuple[int,int]]:
        """Compute and return a path to the target position.
        
        If there is no valid path then returns an empty list.
        """

        cost = np.array(self.entity.map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.map.entities:
            #cost of a blocked position
            if entity.blocks_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y] += 10

        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))

        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        return [(index[0], index[1]) for index in path]
    
class HostileEnemy(BaseAI):
    def __init__(self, entity:Actor):
        super().__init__(entity)
        self.path: List[Tuple[int,int]] = []

    def perform(self):
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y

        distance = max(abs(dx), abs(dy)) # Chebyshev distance

        if self.engine.map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()
        
        return WaitAction(self.entity).perform()