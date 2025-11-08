from typing import List
from gesture_racer.utils.types import PoseData, Command
from gesture_racer.gestures.base import GestureStrategy


class CompositeStrategy(GestureStrategy):
    """Combines multiple strategies. Later strategies can override fields if desired."""

    def __init__(self, strategies: List[GestureStrategy]):
        self.strategies = strategies

    def evaluate(self, pose: PoseData) -> Command:
        cmd = Command()
        for strat in self.strategies:
            sub = strat.evaluate(pose)
            # Merge by OR for booleans
            cmd.forward = cmd.forward or sub.forward
            cmd.backward = cmd.backward or sub.backward
            cmd.left = cmd.left or sub.left
            cmd.right = cmd.right or sub.right
            cmd.brake = cmd.brake or sub.brake
            cmd.fire = cmd.fire or sub.fire
            # Accumulate mouse motion deltas
            cmd.mouse_dx += sub.mouse_dx
            cmd.mouse_dy += sub.mouse_dy
        return cmd