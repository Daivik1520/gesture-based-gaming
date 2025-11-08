from time import time
from gesture_racer.utils.types import PoseData, Command
from gesture_racer.gestures.base import GestureStrategy


class PanicGestureStrategy(GestureStrategy):
    """Triggers an immediate brake and zero mouse when both wrists are above the head for a sustained duration.

    - This acts as a safety/kill-switch gesture.
    - duration_sec controls how long the gesture must be held before engaging.
    """

    def __init__(self, duration_sec: float = 0.8):
        self.duration_sec = duration_sec
        self._start_ts = None

    def evaluate(self, pose: PoseData) -> Command:
        cmd = Command()
        lw = pose.points.get('left_wrist')
        rw = pose.points.get('right_wrist')
        nose = pose.points.get('nose')

        if not (lw and rw and nose):
            self._start_ts = None
            return cmd

        both_above_head = (lw.y < nose.y) and (rw.y < nose.y)
        now = time()

        if both_above_head:
            if self._start_ts is None:
                self._start_ts = now
            if (now - self._start_ts) >= self.duration_sec:
                # Engage panic: brake and zero mouse
                cmd.brake = True
                cmd.mouse_dx = 0.0
                cmd.mouse_dy = 0.0
        else:
            self._start_ts = None

        return cmd