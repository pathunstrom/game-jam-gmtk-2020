from dataclasses import dataclass

from ppb import GameEngine
from ppb import events
from ppb import keycodes
from ppb import systemslib


@dataclass
class Controls:
    forward: bool
    backwards: bool
    left: bool
    right: bool
    rotate_left: bool
    rotate_right: bool


class Controller(systemslib.System):
    forward: bool = False
    backwards: bool = False
    left: bool = False
    right: bool = False
    rotate_left: bool = False
    rotate_right: bool = False

    def __init__(self, *, engine: GameEngine, **kwargs):
        super().__init__(engine=engine, **kwargs)
        engine.register(..., self.add_controls)

    def add_controls(self, event):
        event.controls = Controls(
            self.forward,
            self.backwards,
            self.left,
            self.right,
            self.rotate_left,
            self.rotate_right
        )

    def on_key_pressed(self, event: events.KeyPressed, signal):
        if event.key is keycodes.W:
            self.forward = True
        elif event.key is keycodes.S:
            self.backwards = True
        elif event.key is keycodes.A:
            self.left = True
        elif event.key is keycodes.D:
            self.right = True
        elif event.key is keycodes.Q:
            self.rotate_left = True
        elif event.key is keycodes.E:
            self.rotate_right = True

    def on_key_released(self, event: events.KeyReleased, signal):
        if event.key is keycodes.W:
            self.forward = False
        elif event.key is keycodes.S:
            self.backwards = False
        elif event.key is keycodes.A:
            self.left = False
        elif event.key is keycodes.D:
            self.right = False
        elif event.key is keycodes.Q:
            self.rotate_left = False
        elif event.key is keycodes.E:
            self.rotate_right = False
