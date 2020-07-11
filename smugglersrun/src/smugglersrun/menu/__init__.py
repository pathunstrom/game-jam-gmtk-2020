from ppb import BaseScene, RectangleSprite, Font, Text, Vector
from ppb.buttons import Primary
from ppb.events import ButtonReleased, StartScene

from smugglersrun.sandbox import Sandbox
from smugglersrun.utils import sprite_contains_point

font_path = "smugglersrun/resources/anita_semi_square.ttf"
font_color = (255, 255, 255)


class Menu(BaseScene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        title_font = Font(font_path, size=72)
        button_font = Font(font_path, size=32)
        self.add(
            RectangleSprite(
                image=Text("Smuggler's Run", font=title_font, color=font_color),
                height=2,
                position=Vector(0, 5)
            )
        )

        self.credits_button = RectangleSprite(
                image=Text("Credits", font=button_font, color=font_color),
                height=0.5,
                position=Vector(0, -5)
        )
        self.add(self.credits_button, tags=["button"])

        self.play_game_button = RectangleSprite(
                image=Text("Play", font=button_font, color=font_color),
                height=0.5,
                position=Vector(0, -4)
        )
        self.add(self.play_game_button, tags=["button"])

    def on_button_released(self, event: ButtonReleased, signal):
        if event.button is not Primary:
            return
        for button in self.get(tag="button"):
            if sprite_contains_point(button, event.position):
                if button is self.credits_button:
                    print("Game by Piper Thunstrom")
                    print("Font: Anita semi-square by Gustavo Paz")
                    print("Font used under CC-SA 4.0")
                elif button is self.play_game_button:
                    signal(StartScene(Sandbox))
