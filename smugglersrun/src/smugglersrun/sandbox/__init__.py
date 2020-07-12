from dataclasses import dataclass
from itertools import product
from math import floor
from random import random
from random import uniform
from time import perf_counter
from typing import Callable

import ppb

from smugglersrun import font
from smugglersrun.perlin import PerlinNoiseFactory
from smugglersrun.systems import Controls
from smugglersrun.utils import box_collide

# Game design assumptions:
# 1. 1 unit ~= 35m
# 10KM = 285 unit (approx)


CONFIG_STARTING_DAMAGE = 0
CONFIG_DAMAGE_CHANCE_INCREASE = 0.1

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

        if self.control_active(self.components["rotate_left"], controls, now):
            self.rotate(self.CONFIG_ROTATION_PER_FRAME)
        if self.control_active(self.components["rotate_right"], controls, now):
            self.rotate(-self.CONFIG_ROTATION_PER_FRAME)

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

        damage_chance = 0
        for mine in event.scene.get(kind=ShockMine):
            if box_collide(self, mine):
                damage_chance += CONFIG_DAMAGE_CHANCE_INCREASE

        component: Component
        for component in self.components.values():
            random_val = random()
            if random_val <= damage_chance:
                component.damage += 1

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
        print(f"min: {min(self.debug_values)}, max: {max(self.debug_values)}, mean: {sum(self.debug_values) / len(self.debug_values)}")


class ShockMine(ppb.Sprite):
    image = ppb.Image("smugglersrun/resources/shock-mine.png")
    size = 0.25


class TimeDisplay(ppb.RectangleSprite):
    height = 0.5
    time = 0

    @property
    def image(self):
        minutes = self.time // 60
        seconds = floor(self.time % 60)
        fractions = self.time % 1
        result = f"{minutes:02.0f}:{seconds:02.0f}:{fractions * 100:02.0f}"
        return ppb.Text(result, font=font.button, color=font.color)


class Countdown(ppb.Sprite):
    height = 2
    time = 0

    @property
    def image(self):
        return ppb.Text(str(int(self.time)), font=font.title, color=font.color)


class Sandbox(ppb.BaseScene):
    CONFIG_DENSITY_MODIFER = 3
    CONFIG_PENALTY_START_MULTIPLIER = 5
    CONFIG_PENALTY_OOB_MULTIPLIER = 0.1
    CONFIG_BONUS_TIME = 3
    remaining_time = 0
    start_timer = 5
    end_timer = 5

    def __init__(self, *, difficulty_level:int = 1, components: dict = None, remaining_time: float = 30):
        super().__init__()
        self.difficulty_level = difficulty_level
        forward = ppb.Sprite(opacity=0)
        self.add(forward)
        if components is not None:
            self.add(Player(forward_thrust_sprite=forward, components=components), tags=["player"])
        else:
            self.add(Player(forward_thrust_sprite=forward), tags=["player"])

        for root_y in range(10, 291, 20):
            chunk_root = ppb.Vector(0, root_y)
            for _ in range(int(difficulty_level * self.CONFIG_DENSITY_MODIFER)):
                x = uniform(-10, 10)
                y = uniform(-10, 10)
                self.add(ShockMine(position=chunk_root + ppb.Vector(x, y)))
            # self.add(ppb.Sprite(image=ppb.Square(80, 200, 60), position=(0, y), size=0.25))
            for x_pos, y_mod in product((-10, 10), range(-10, 10, 3)):
                self.add(ppb.Sprite(
                    image=ppb.Image("smugglersrun/resources/beacon.png"),
                    position=(x_pos, root_y + y_mod),
                    size=0.25
                ))
        self.add(ppb.RectangleSprite(image=ppb.Square(100, 200, 75), position=(0, 285)), tags=["finish"])
        self.add(TimeDisplay(time=remaining_time), tags=["timer"])
        self.add(Countdown(time=self.start_timer), tags=["countdown", "start"])
        self.add(Countdown(time=self.start_timer), tags=["countdown", "end"])
        self.remaining_time = remaining_time
        self.started = perf_counter()
        self.finished = False

    def on_pre_render(self, _, __):
        cam = self.main_camera
        player = next(self.get(kind=Player))
        cam.position = player.position

        time_display: TimeDisplay = next(self.get(kind=TimeDisplay))
        time_display.position = cam.position + ppb.Vector(8, -6)
        time_display.time = self.remaining_time if self.remaining_time > 0 else 0

        countdown = next(self.get(tag="start"))
        if self.start_timer > 0:
            countdown.position = cam.position + ppb.Vector(0, 2)
            countdown.time = self.start_timer
            countdown.opacity = 255
        else:
            countdown.opacity = 0

        countdown = next(self.get(tag="end"))
        if (self.finished or self.remaining_time <= 0) and  self.end_timer > 0:
            countdown.position = cam.position + ppb.Vector(0, 2)
            countdown.time = self.end_timer
            countdown.opacity = 255
        else:
            countdown.opacity = 0

    def on_update(self, update: ppb.events.Update, signal_event):
        player:Player = next(self.get(kind=Player))
        finish = next(self.get(tag="finish"))

        if self.start_timer > 0:
            self.start_timer -= update.time_delta
            if player.position.x >= 5:
                self.remaining_time -= update.time_delta * self.CONFIG_PENALTY_START_MULTIPLIER
        elif not self.finished and self.remaining_time > 0:
            if player.position.y >= finish.position.y:
                self.finished = True
            elif -11 <= player.position.x <= 11:
                self.remaining_time -= update.time_delta * self.CONFIG_PENALTY_OOB_MULTIPLIER
            self.remaining_time -= update.time_delta
        elif self.end_timer > 0:
            self.end_timer -= update.time_delta
        else:
            if self.remaining_time <= 0:
                signal_event(ppb.events.StopScene())
            else:
                signal_event(
                    ppb.events.ReplaceScene(
                        Sandbox,
                        kwargs={
                            "difficulty_level": self.difficulty_level + 1,
                            "components": player.components,
                            "remaining_time": self.remaining_time + self.difficulty_level * self.CONFIG_BONUS_TIME,
                        }
                    )
                )
