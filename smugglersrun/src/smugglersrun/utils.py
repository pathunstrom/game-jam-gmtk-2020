from typing import Union

from ppb import Sprite, RectangleSprite, Vector

SpritesType = Union[Sprite, RectangleSprite]


def sprite_contains_point(sprite: SpritesType, point: Vector):
    return (sprite.left < point.x < sprite.right
            and sprite.bottom < point.y < sprite.top)
