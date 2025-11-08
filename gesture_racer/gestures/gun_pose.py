import math
from typing import Optional
from gesture_racer.utils.types import PoseData, Command, PosePoint
from gesture_racer.gestures.base import GestureStrategy


def angle(a: PosePoint, b: PosePoint, c: PosePoint) -> Optional[float]:
    """Angle at point b formed by points a-b-c in degrees."""
    if not a or not b or not c:
        return None
    v1 = (a.x - b.x, a.y - b.y)
    v2 = (c.x - b.x, c.y - b.y)
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    if mag1 == 0 or mag2 == 0:
        return None
    cosang = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cosang))


class GunPoseStrategy(GestureStrategy):
    """Detects a gun-holding pose and issues a fire command.

    Heuristics:
    - Both elbows are bent (angle at elbow below threshold)
    - Wrists proximity within a distance threshold (hands together near center)
    These are simple, robust cues for "holding up and aiming" in 2D.
    """

    def __init__(self, elbow_bent_threshold_deg: float = 70.0, wrist_distance_px: int = 120):
        self.elbow_bent_threshold_deg = elbow_bent_threshold_deg
        self.wrist_distance_px = wrist_distance_px

    def evaluate(self, pose: PoseData) -> Command:
        pts = pose.points
        ls = pts.get('left_shoulder')
        rs = pts.get('right_shoulder')
        le = pts.get('left_elbow')
        re = pts.get('right_elbow')
        lw = pts.get('left_wrist')
        rw = pts.get('right_wrist')

        cmd = Command()

        if all([ls, rs, le, re, lw, rw]):
            # Elbow bend angles
            left_angle = angle(ls, le, lw)
            right_angle = angle(rs, re, rw)

            # Distance between wrists
            dx = lw.x - rw.x
            dy = lw.y - rw.y
            wrist_dist = math.sqrt(dx * dx + dy * dy)

            elbows_bent = False
            if left_angle is not None and right_angle is not None:
                elbows_bent = (left_angle < self.elbow_bent_threshold_deg) and (
                    right_angle < self.elbow_bent_threshold_deg)

            hands_together = wrist_dist < self.wrist_distance_px

            if elbows_bent and hands_together:
                cmd.fire = True

        return cmd