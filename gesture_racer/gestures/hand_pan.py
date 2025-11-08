from gesture_racer.utils.types import PoseData, Command
from gesture_racer.gestures.base import GestureStrategy
from gesture_racer.utils.filters import EmaFilter


class HandPanStrategy(GestureStrategy):
    """Pan screen/camera based on average wrist position relative to frame center.

    - Uses left/right wrist positions; if one is missing, uses the available wrist.
    - Maps horizontal and vertical offsets to mouse_dx/dy per frame.
    - Applies a pixel dead-zone to reduce jitter and clamps max movement per frame.
    - Optional invert_y to match subjective camera feel.
    """

    def __init__(self,
                 sensitivity: float = 1.2,
                 dead_zone_px: int = 25,
                 max_px_per_frame: float = 30.0,
                 invert_y: bool = False,
                 use_velocity: bool = False,
                 ema_alpha: float = 0.3,
                 neutral_center: bool = True):
        self.sensitivity = sensitivity
        self.dead_zone_px = dead_zone_px
        self.max_px_per_frame = max_px_per_frame
        self.invert_y = invert_y
        self.use_velocity = use_velocity
        self._ema_dx = EmaFilter(alpha=ema_alpha)
        self._ema_dy = EmaFilter(alpha=ema_alpha)
        self.neutral_center = neutral_center
        self._neutral_x = None
        self._neutral_y = None
        self._last_avg_x = None
        self._last_avg_y = None

    def evaluate(self, pose: PoseData) -> Command:
        cmd = Command()
        lw = pose.points.get('left_wrist')
        rw = pose.points.get('right_wrist')

        # Choose average of available wrists
        xs = []
        ys = []
        if lw:
            xs.append(lw.x)
            ys.append(lw.y)
        if rw:
            xs.append(rw.x)
            ys.append(rw.y)

        if not xs:
            return cmd

        avg_x = sum(xs) / len(xs)
        avg_y = sum(ys) / len(ys)

        # Neutral center calibration: first frame sets neutral unless disabled
        if self._neutral_x is None or self._neutral_y is None:
            if self.neutral_center:
                self._neutral_x = pose.width / 2.0
                self._neutral_y = pose.height / 2.0
            else:
                self._neutral_x = pose.width / 2.0
                self._neutral_y = pose.height / 2.0

        center_x = self._neutral_x
        center_y = self._neutral_y

        if self.use_velocity and self._last_avg_x is not None and self._last_avg_y is not None:
            # Velocity mode: use frame-to-frame wrist movement
            offset_x = avg_x - self._last_avg_x
            offset_y = avg_y - self._last_avg_y
        else:
            # Position mode: use distance from neutral center
            offset_x = avg_x - center_x
            offset_y = avg_y - center_y

        # Dead-zone
        if abs(offset_x) <= self.dead_zone_px and abs(offset_y) <= self.dead_zone_px:
            return cmd

        # Normalize to [-1, 1] if using position; else scale raw velocity directly
        if not self.use_velocity:
            norm_x = offset_x / (pose.width / 2.0)
            norm_y = offset_y / (pose.height / 2.0)
            dx = norm_x * (self.max_px_per_frame * self.sensitivity)
            dy = norm_y * (self.max_px_per_frame * self.sensitivity)
        else:
            dx = offset_x * (self.sensitivity * 0.15)  # tune velocity gain
            dy = offset_y * (self.sensitivity * 0.15)

        if self.invert_y:
            dy = -dy

        # EMA smoothing
        dx = self._ema_dx.update(dx)
        dy = self._ema_dy.update(dy)

        # Clamp
        if dx > self.max_px_per_frame:
            dx = self.max_px_per_frame
        elif dx < -self.max_px_per_frame:
            dx = -self.max_px_per_frame

        if dy > self.max_px_per_frame:
            dy = self.max_px_per_frame
        elif dy < -self.max_px_per_frame:
            dy = -self.max_px_per_frame

        cmd.mouse_dx = dx
        cmd.mouse_dy = dy

        # Save last positions for velocity mode
        self._last_avg_x = avg_x
        self._last_avg_y = avg_y
        return cmd