from gesture_racer.utils.types import PoseData, Command
from gesture_racer.gestures.base import GestureStrategy


class HandTurnStrategy(GestureStrategy):
    """Set left/right intents based on horizontal wrist position relative to frame center.

    - Uses average of available wrists (left/right). If only one wrist visible, uses it.
    - Applies a dead-zone to avoid unintended turns when hands are near center.
    - Sensitivity controls how much offset triggers a turn; this strategy produces booleans, not mouse.
    - Optional invert_x to flip left/right mapping if needed.
    """

    def __init__(self, dead_zone_px: int = 40, invert_x: bool = False, hysteresis_px: int = 20):
        self.dead_zone_px = dead_zone_px
        self.invert_x = invert_x
        self.hysteresis_px = hysteresis_px
        self._current_left = False
        self._current_right = False

    def evaluate(self, pose: PoseData) -> Command:
        cmd = Command()
        lw = pose.points.get('left_wrist')
        rw = pose.points.get('right_wrist')

        xs = []
        if lw:
            xs.append(lw.x)
        if rw:
            xs.append(rw.x)

        if not xs:
            return cmd

        avg_x = sum(xs) / len(xs)
        center_x = pose.width / 2.0
        offset_x = avg_x - center_x

        # Within dead-zone: keep current state but don't trigger new turns
        if abs(offset_x) <= self.dead_zone_px:
            cmd.left = self._current_left
            cmd.right = self._current_right
            return cmd

        # Map offset to left/right boolean
        # Apply hysteresis to prevent flicker around threshold
        if offset_x > (self.dead_zone_px + self.hysteresis_px):
            go_right = True
            go_left = False
        elif offset_x < -(self.dead_zone_px + self.hysteresis_px):
            go_right = False
            go_left = True
        else:
            # Within hysteresis band: keep previous state
            go_left = self._current_left
            go_right = self._current_right

        if self.invert_x:
            go_left, go_right = go_right, go_left

        self._current_left = go_left
        self._current_right = go_right
        cmd.left = go_left
        cmd.right = go_right
        return cmd