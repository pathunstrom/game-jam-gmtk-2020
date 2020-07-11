from typing import Union

from ppb import Sprite, RectangleSprite, Vector

SpritesType = Union[Sprite, RectangleSprite]


def sprite_contains_point(sprite: SpritesType, point: Vector):
    return (sprite.left < point.x < sprite.right
            and sprite.bottom < point.y < sprite.top)


def box_collide(left: SpritesType, right: SpritesType):
    return (
        max(left.right, right.right) - min(left.left, right.left) < left.width + right.width
        and max(left.top, right.top) - min(left.bottom, right.bottom) < left.height + right.height
    )
