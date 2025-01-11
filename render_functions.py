from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod.console import Console
    from game_map import GameMap
    from engine import Engine

def get_names_at(x:int, y:int, map:GameMap) -> str:
    if not map.in_bounds(x, y) or not map.visible[x, y]:
        return ""
    
    names = ", ".join(
        entity.name for entity in map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()

def render_bar(
        console:Console, current_value:int, max_value:int, total_width:int
) -> None:
    bar_width = int(float(current_value)/max_value * total_width)

    console.draw_rect(x=0, y=45, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=1, y=45, string=f"HP: {current_value}/{max_value}", fg=color.bar_text
    )

def render_names_at_mouse(
        console:Console, x:int, y:int, engine:Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_position

    names_at_mouse = get_names_at(mouse_x, mouse_y, engine.map)

    console.print(x, y, string=names_at_mouse)