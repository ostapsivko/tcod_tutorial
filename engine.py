from __future__ import annotations

from typing import TYPE_CHECKING

import lzma
import pickle

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from render_functions import render_bar, render_names_at_mouse
from message_log import MessageLog

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap

class Engine:

    map:GameMap

    def __init__(self, player:Actor):
        self.player = player
        self.message_log = MessageLog()
        self.mouse_position = (0,0)

    def handle_enemy_turns(self) -> None:
        for entity in set(self.map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass

    def render(self, console:Console) -> None:
        self.map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_bar(
            console=console, 
            current_value=self.player.fighter.hp,
            max_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_names_at_mouse(console=console, x=21, y=44, engine=self)

    def update_fov(self) -> None:
        """Recompute the visible area based on the player current point of view"""
        self.map.visible[:] = compute_fov(
            self.map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8
        )

        self.map.explored |= self.map.visible

    def save_as(self, filename:str) -> None:
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)