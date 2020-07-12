from ppb import BaseScene, RectangleSprite, Text, Vector
from ppb.buttons import Primary
from ppb.events import ButtonReleased, StartScene, StopScene

from smugglersrun import font
from smugglersrun.sandbox import Sandbox
from smugglersrun.utils import sprite_contains_point


class Display(RectangleSprite):
    height = 0.5
    text: str = "Default Text"
    font = font.button

    @property
    def image(self):
        return Text(self.text, font=self.font, color=font.color)


class LargeDisplay(Display):
    height = 2
    font = font.title


class Credits(BaseScene):

    def __init__(self):
        super().__init__()
        self.back_button = Display(text="Back", position=(-10, -5.5))
        self.add(self.back_button, tags=["back_button"])

        self.add(Display(text="Game Design and Programming By:", position=Vector(-6, 5)))
        self.add(Display(text="Piper Thunstrom", position=Vector(-6, 4)))

        self.add(Display(text="Font Anita Semi-Square By:", position=Vector(-6.75, 2.5)))  # Last: 7 6.5
        self.add(Display(text="Gustavo Paz", position=Vector(-6.5, 1.5)))  # Last 7 6
        self.add(Display(text="Used under CC-SA 4.0", position=Vector(4, 1.5)))

        self.add(Display(text="Images by:", position=(-9, 0)))  # Last: 7
        self.add(Display(text="Kenney studios", position=(-6, -1)))

    def on_button_released(self, event: ButtonReleased, signal):
        if event.button is not Primary:
            return
        if sprite_contains_point(self.back_button, event.position):
            signal(StopScene())


class Menu(BaseScene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(LargeDisplay(text="Smuggler's Run", position=Vector(0, 5)))

        self.credits_button = Display(text="Credits", position=Vector(0, -5))
        self.add(self.credits_button, tags=["button"])

        self.play_game_button = Display(text="Play", position=Vector(0, -4))
        self.add(self.play_game_button, tags=["button"])

    def on_button_released(self, event: ButtonReleased, signal):
        if event.button is not Primary:
            return
        for button in self.get(tag="button"):
            if sprite_contains_point(button, event.position):
                if button is self.credits_button:
                    signal(StartScene(Credits))
                    print("Game by Piper Thunstrom")
                    print("Font: Anita semi-square by Gustavo Paz")
                    print("Font used under CC-SA 4.0")
                elif button is self.play_game_button:
                    signal(StartScene(Sandbox))
