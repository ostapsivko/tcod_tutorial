from __future__ import annotations

import copy
import lzma
import pickle
import traceback
from typing import Optional

import tcod
import tcod.constants

import color
from engine import Engine
import entity_factories
import input_handlers
from procgen import generate_dungeon

background_image = tcod.image.load("menu_background.png")[:,:,:3]

def new_game() -> Engine:
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2
    max_items_per_room = 2

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player)

    engine.map = generate_dungeon(
        max_rooms=max_rooms, 
        room_min_size=room_min_size, 
        room_max_size=room_max_size, 
        map_width=map_width, 
        map_height=map_height, 
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room, 
        engine=engine)
    
    engine.update_fov()

    engine.message_log.add_message("Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text)

    return engine

class MainMenu(input_handlers.BaseEventHandler):

    def on_render(self, console):
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOMBS OF THE ANCIENT KINGS",
            fg=color.menu_title,
            alignment=tcod.constants.CENTER,
        )

        console.print(
            console.width // 2,
            console.height - 2,
            "By Azdabka",
            fg=color.menu_title,
            alignment=tcod.constants.CENTER,
        )

        menu_width = 24

        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.constants.CENTER,
                bg_blend=tcod.constants.BKGND_ALPH,
            )

    def ev_keydown(self, event) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game found.")
            except Exception as exc:
                traceback.print_exc()
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            return input_handlers.MainGameEventHandler(new_game())
        
        return None
    
def load_game(filename:str) -> Engine:
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine