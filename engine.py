from typing import Set, Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from actions import EscapeAction, MovementAction
from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler

class Engine:
    def __init__(self, event_handler:EventHandler, map:GameMap, player:Entity):
        self.event_handler = event_handler
        self.player = player
        self.map = map
        self.update_fov()

    def handle_events(self, events:Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)
            self.handle_enemy_turns()
            self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.map.entities - {self.player}:
            print(f'The entity {entity.name} wonders when it will get to take a real turn')

    def render(self, console:Console, context:Context) -> None:
        self.map.render(console)
        
        context.present(console)

        console.clear()

    def update_fov(self) -> None:
        """Recompute the visible area based on the player current point of view"""
        self.map.visible[:] = compute_fov(
            self.map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8
        )

        self.map.explored |= self.map.visible