from typing import Optional

import tcod.event

from actions import Action, EscapeAction, BumpAction

class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        if key == tcod.event.KeySym.UP:
            action = BumpAction(0, -1)
        elif key == tcod.event.KeySym.DOWN:
            action = BumpAction(0, 1)
        elif key == tcod.event.KeySym.LEFT:
            action = BumpAction(-1, 0)
        elif key == tcod.event.KeySym.RIGHT:
            action = BumpAction(1, 0)

        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction()

        #no valid input
        return action