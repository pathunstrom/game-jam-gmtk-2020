from dataclasses import dataclass
from pprint import pprint
from random import random
from time import perf_counter
from typing import Callable

import ppb

from smugglersrun.systems import Controls
from smugglersrun.perlin import PerlinNoiseFactory
# Game design assumptions:
# 1. 1 unit ~= 35m
# 10KM = 285 unit (approx)


CONFIG_STARTING_DAMAGE = 15

@dataclass
class Update(ppb.events.Update):
    controls: Controls = None


@dataclass
class Component:
    control_name: str
    operable: bool = True
    damage: int = 0
    CONFIG_MAX_DAMAGE = 100
    randomizer: Callable[[float], float] = lambda _, __: random()


main_random = PerlinNoiseFactory(1)
retro_random = PerlinNoiseFactory(1)
left_random = PerlinNoiseFactory(1)
right_random = PerlinNoiseFactory(1)
rot_left_random = PerlinNoiseFactory(1)
rot_right_random = PerlinNoiseFactory(1)


class Player(ppb.Sprite):
    image = ppb.Image("smugglersrun/resources/dev_ship.png")
    basis = ppb.Vector(0, 1)

    velocity = ppb.Vector(0, 0)
    acceleration = ppb.Vector(0, 0)
    rotation_velocity = 0
    components = {
        "forward": Component("forward", damage=CONFIG_STARTING_DAMAGE, randomizer=lambda x: (main_random(x) + 1) / 2),
        "backwards": Component("backwards", damage=CONFIG_STARTING_DAMAGE, randomizer=lambda x: (retro_random(x) + 1) / 2),
        "left": Component("left", damage=CONFIG_STARTING_DAMAGE, randomizer=lambda x: (left_random(x) + 1) / 2),
        "right": Component("right", damage=CONFIG_STARTING_DAMAGE, randomizer=lambda x: (right_random(x) + 1) / 2),
        "rotate_left": Component("rotate_left", damage=CONFIG_STARTING_DAMAGE, randomizer=lambda x: (rot_left_random(x) + 1) / 2),
        "rotate_right": Component("rotate_right", damage=CONFIG_STARTING_DAMAGE, randomizer=lambda x: (rot_right_random(x) + 1) / 2)
    }
    forward_thrust_sprite: ppb.Sprite

    CONFIG_THRUST_FORWARD = 3
    CONFIG_THRUST_LATERAL = 1.5
    CONFIG_THRUST_REVERSE = 1.5
    CONFIG_ROTATION_PER_FRAME = 2.5

    debug_values = []

    def on_update(self, event: Update, _):
        acceleration = ppb.Vector(0, 0)
        now = perf_counter()
        controls = event.controls

        if self.control_active(self.components["forward"], controls, now):
            acceleration += self.facing.scale_to(self.CONFIG_THRUST_FORWARD)
            self.forward_thrust_sprite.opacity = 255
        else:
            self.forward_thrust_sprite.opacity = 0

        if self.control_active(self.components["backwards"], controls, now):
            acceleration += self.facing.scale_to(self.CONFIG_THRUST_REVERSE) * -1

        if self.control_active(self.components["right"], controls, now):
            acceleration += self.facing.rotate(-90).scale_to(self.CONFIG_THRUST_LATERAL)

        if self.control_active(self.components["left"], controls, now):
            acceleration += self.facing.rotate(90).scale_to(self.CONFIG_THRUST_LATERAL)

        self.velocity += acceleration * event.time_delta
        self.position += self.velocity * event.time_delta

        if event.controls.rotate_left:
            self.rotate(self.CONFIG_ROTATION_PER_FRAME)
        if event.controls.rotate_right:
            self.rotate(-self.CONFIG_ROTATION_PER_FRAME)

    def on_pre_render(self, event, signal):
        self.forward_thrust_sprite.position = self.position + (self.facing * -1)

    def control_active(self, component, controls, now):
        now = perf_counter()
        _random = component.randomizer(now / 5)
        self.debug_values.append(_random)
        malfunction = _random < component.damage / component.CONFIG_MAX_DAMAGE
        control_val = getattr(controls, component.control_name)
        return (control_val and not malfunction) or (not control_val and malfunction)

    def on_quit(self, _, __):
        pprint(self.debug_values)
        print(f"min: {min(self.debug_values)}, max: {max(self.debug_values)}, mean: {sum(self.debug_values) / len(self.debug_values)}")


class ShockMine(ppb.Sprite):
    image = ppb.Square(120, 130, 225)


class Sandbox(ppb.BaseScene):

    def __init__(self):
        super().__init__()
        forward = ppb.Sprite(opacity=0)
        self.add(forward)
        self.add(Player(forward_thrust_sprite=forward), tags=["player"])
        for y in range(5, 286, 10):
            self.add(ShockMine(position=(0, y)))
            # self.add(ppb.Sprite(image=ppb.Square(80, 200, 60), position=(0, y), size=0.25))
            self.add(ppb.Sprite(image=ppb.Square(175, 60, 75), position=(10, y), size=0.25))
            self.add(ppb.Sprite(image=ppb.Square(175, 60, 75), position=(-10, y), size=0.25))
        self.add(ppb.Sprite(image=ppb.Square(100, 200, 75), position=(0, 285)), tags=["finish"])
        self.started = perf_counter()
        self.finished = False

    def on_pre_render(self, _, __):
        cam = self.main_camera
        player = next(self.get(kind=Player))
        cam.position = player.position

    def on_update(self, _, __):
        player = next(self.get(kind=Player))
        finish = next(self.get(tag="finish"))
        if not self.finished and player.position.y >= finish.position.y:
            print(f"Run finished: {perf_counter() - self.started}s")
            self.finished = True
