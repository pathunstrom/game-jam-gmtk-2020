from dataclasses import dataclass

from ppb import BaseScene
from ppb.systemslib import System


@dataclass
class DistanceUpdate:
    distance: float
    scene: BaseScene


class ScoringSystem(System):
    firm_score = 0
    current_level_distance = 0
    current_level_multiplier = 0
    top_score = 0

    def on_scene_started(self, event, signal):
        self.merge_scores()
        s = event.scene
        if getattr(s, "needs_top_score"):
            s.top_score = self.top_score

    def on_distance_update(self, e: DistanceUpdate, signal):
        self.current_level_score