"""
A space race game for the GMTK Gamejam 2020
"""
import ppb

from smugglersrun import menu
from smugglersrun.systems import Controller


def main():
    ppb.run(
        starting_scene=menu.Menu,
        title='Smuggler\'s Run',
        resolution=(1280, 720),
        systems=[Controller]
    )
