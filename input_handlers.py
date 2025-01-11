from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING, Tuple

import tcod.constants
import tcod.event

import actions
from actions import Action, BumpAction, WaitAction, PickupAction

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

MOVE_KEYS = {
    #arrow keys
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    #numpad
    tcod.event.KeySym.KP_1:(-1,1),
    tcod.event.KeySym.KP_2:(0,1),
    tcod.event.KeySym.KP_3:(1,1),
    tcod.event.KeySym.KP_4:(-1,0),
    tcod.event.KeySym.KP_6:(1,0),
    tcod.event.KeySym.KP_7:(-1,-1),
    tcod.event.KeySym.KP_8:(0,-1),
    tcod.event.KeySym.KP_9:(1,-1),
    #vi keys
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP:-1,
    tcod.event.KeySym.DOWN:1,
    tcod.event.KeySym.PAGEUP:-10,
    tcod.event.KeySym.PAGEDOWN:10,
}

class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine:Engine):
        self.engine = engine

    def handle_events(self, event:tcod.event.Event) -> None:
        self.handle_action(self.dispatch(event))

    def handle_action(self, action:Optional[Action]) -> bool:
        if action is None:
            return False
        
        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event):
        if self.engine.map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_position = event.tile.x, event.tile.y

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()
    
    def on_render(self, console:tcod.console.Console) -> None:
        self.engine.render(console=console)

class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.v:
            self.engine.event_handler = HistoryViewer(self.engine)
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.i:
            self.engine.event_handler = InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.d:
            self.engine.event_handler = InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            self.engine.event_handler = LookHandler(self.engine)

        #no valid input
        return action
    
class GameOverEventHandler(EventHandler):
    def ev_keydown(self, event:tcod.event.Event):
        if event.sym == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
    
class HistoryViewer(EventHandler):
    def __init__(self, engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console):
        super().on_render(console)
    
        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        log_console.draw_frame(0,0,log_console.width, log_console.height)
        log_console.print_box(0,0,log_console.width, 1, "┤Message history├", alignment=tcod.constants.CENTER)

        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[:self.cursor + 1], 
        )

        log_console.blit(console, 3,3)

    def ev_keydown(self, event):
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]

            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1
        else:
            self.engine.event_handler = MainGameEventHandler(self.engine)

class AskUserEventHandler(EventHandler):
    def handle_action(self, action):
        if super().handle_action(action):
            self.engine.event_handler = MainGameEventHandler(self.engine)
            return True
        return False
    
    def ev_keydown(self, event):
        if event.sym in {
            tcod.event.KMOD_LSHIFT,
            tcod.event.KMOD_RSHIFT,
            tcod.event.KMOD_LCTRL,
            tcod.event.KMOD_RCTRL,
            tcod.event.KMOD_LALT,
            tcod.event.KMOD_RALT,
        }:
            return None
        return self.on_exit()
    
    def ev_mousebuttondown(self, event):
        return self.on_exit()
    
    def on_exit(self) -> Optional[Action]:
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return None
    
class InventoryEventHandler(AskUserEventHandler):
    TITLE = "<missing title>"

    def on_render(self, console):
        super().on_render(console)
    
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255,255,255),
            bg=(0,0,0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event):
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    
    def on_item_selected(self, item:Item) -> Optional[Action]:
        raise NotImplementedError()
    
class InventoryActivateHandler(InventoryEventHandler):
    TITLE = "Select an item to use"

    def on_item_selected(self, item):
        return item.consumable.get_action(self.engine.player)
    
class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"

    def on_item_selected(self, item:Item) -> Optional[Action]:
        return actions.DropAction(self.engine.player, item)
    
class SelectIndexHandler(AskUserEventHandler):
    def __init__(self, engine):
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_position = player.x, player.y

    def on_render(self, console):
        super().on_render(console)
        x, y = self.engine.mouse_position
        console.tiles_rgb["bg"][x,y] = color.white
        console.tiles_rgb["fg"][x,y] = color.black

    def ev_keydown(self, event:tcod.event.KeyDown):
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1 #modifier keys will speed up the key movement

            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_position
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            x = max(0, min(x, self.engine.map.width - 1))
            y = max(0, min(y, self.engine.map.height - 1))
            self.engine.mouse_position = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_position)
        
        return super().ev_keydown(event)
    
    def ev_mousebuttondown(self, event:tcod.event.MouseButtonDown):
        if self.engine.map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)
    
    def on_index_selected(self, x:int, y:int) -> Optional[Action]:
        raise NotImplementedError()
    
class LookHandler(SelectIndexHandler):
    def on_index_selected(self, x, y):
        self.engine.event_handler = MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    def __init__(self, engine, callback: Callable[[Tuple[int,int]], Optional[Action]]):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x, y):
        return self.callback((x, y))
    
class AreaRangedAttackHandler(SelectIndexHandler):
    def __init__(
            self, 
            engine:Engine,
            radius:int,
            callback:Callable[[Tuple[int,int]], Optional[Action]]
        ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console:tcod.console.Console):
        super().on_render(console)

        x, y = self.engine.mouse_position

        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height = self.radius ** 2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x, y):
        return self.callback((x, y))