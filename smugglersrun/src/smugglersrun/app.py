"""
A space race game for the GMTK Gamejam 2020
"""
import ppb
from ppb import assetlib

from smugglersrun import menu
from smugglersrun.splash import Splash
from smugglersrun.systems import Controller, BackgroundMusicController


def main():
    ppb.run(
        starting_scene=Splash,
        scene_kwargs={"next_scene": menu.Menu, "package": "smugglersrun"},
        title='Smuggler\'s Run',
        resolution=(1280, 720),
        systems=[Controller],
        basic_systems=(
            ppb.systems.Renderer,
            ppb.systems.Updater,
            ppb.systems.EventPoller,
            BackgroundMusicController,
            assetlib.AssetLoadingSystem
        )
    )
