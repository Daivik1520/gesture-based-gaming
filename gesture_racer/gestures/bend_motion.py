from gesture_racer.utils.types import PoseData, Command
from gesture_racer.gestures.base import GestureStrategy


class BendMotionStrategy(GestureStrategy):
    """Detect forward/backward movement based on torso lean.

    Uses the relative depth (z) between shoulders and hips:
    - If shoulders are closer to the camera than hips by a threshold -> forward
    - If shoulders are farther than hips -> backward
    Note: MediaPipe z is approximately meters toward camera (negative values are closer).
    """

    def __init__(self, lean_threshold: float = 0.10):
        self.lean_threshold = lean_threshold

    def evaluate(self, pose: PoseData) -> Command:
        pts = pose.points
        ls = pts.get('left_shoulder')
        rs = pts.get('right_shoulder')
        lh = pts.get('left_hip')
        rh = pts.get('right_hip')

        cmd = Command()
        if all([ls, rs, lh, rh]):
            shoulders_z = (ls.z + rs.z) / 2.0
            hips_z = (lh.z + rh.z) / 2.0
            # More negative -> closer to camera
            delta = shoulders_z - hips_z

            if delta < -self.lean_threshold:
                cmd.forward = True
            elif delta > self.lean_threshold:
                cmd.backward = True

        return cmd