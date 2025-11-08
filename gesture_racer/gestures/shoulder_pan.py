from gesture_racer.utils.types import PoseData, Command
from gesture_racer.gestures.base import GestureStrategy


class ShoulderPanStrategy(GestureStrategy):
    """Pan camera based on relative shoulder depth (z).

    Rule requested:
    - Turn RIGHT when the RIGHT shoulder is more back than the LEFT (rs.z > ls.z)
    - Turn LEFT when the LEFT shoulder is more back than the RIGHT (ls.z > rs.z)

    MediaPipe Pose z note: more negative is closer to camera; more positive is farther (back).
    We use the delta_z = rs.z - ls.z and map it to mouse_dx with a dead-zone and clamp.
    """

    def __init__(self, z_sensitivity_px_per_unit: float = 400.0, dead_zone_z: float = 0.03,
                 max_px_per_frame: float = 30.0):
        # How many pixels to move per unit of z difference
        self.z_sensitivity = z_sensitivity_px_per_unit
        self.dead_zone_z = dead_zone_z
        self.max_px_per_frame = max_px_per_frame

    def evaluate(self, pose: PoseData) -> Command:
        cmd = Command()
        ls = pose.points.get('left_shoulder')
        rs = pose.points.get('right_shoulder')
        if not (ls and rs):
            return cmd

        delta_z = rs.z - ls.z  # positive => right shoulder farther back => pan right

        # Dead-zone to avoid jitter
        if abs(delta_z) <= self.dead_zone_z:
            return cmd

        dx = delta_z * self.z_sensitivity

        # Clamp
        if dx > self.max_px_per_frame:
            dx = self.max_px_per_frame
        elif dx < -self.max_px_per_frame:
            dx = -self.max_px_per_frame

        cmd.mouse_dx = dx
        cmd.mouse_dy = 0.0
        return cmd