from typing import Tuple

import numpy as np #type:ignore

graphic_dt = np.dtype(
    [
        ("ch", np.int32), #Unicode codepoint
        ("fg", "3B"), #3 unsigned bytes, for RGB colors
        ("bg", "3B")
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", np.bool),
        ("transparent", np.bool),
        ("dark", graphic_dt),
        ("light", graphic_dt)
    ]
)

def new_tile(
        *,
        walkable:int,
        transparent:int,
        dark:Tuple[int, Tuple[int,int,int], Tuple[int,int,int]],
        light:Tuple[int, Tuple[int,int,int], Tuple[int,int,int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

#represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0,0,0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True, 
    transparent=True, 
    dark=(ord(" "), (255,255,255), (50,50,150)),
    light=(ord(" "), (255,255,255), (200,180,50)),
)

wall = new_tile(
    walkable=False, 
    transparent=False, 
    dark=(ord(" "), (255,255,255), (0,0,100)),
    light=(ord(" "), (255,255,255), (130,110,50)),
)

down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0,0,100), (50,50,150)),
    light=(ord(">"), (255,255,255), (200,180,50)),
)