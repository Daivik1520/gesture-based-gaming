from abc import ABC, abstractmethod
from time import time
from typing import Optional
from gesture_racer.utils.types import Command


class KeyboardMouseInput(ABC):
    @abstractmethod
    def press(self, key: str):
        pass

    @abstractmethod
    def release(self, key: str):
        pass

    @abstractmethod
    def click_mouse(self, button: str = 'left'):
        pass

    @abstractmethod
    def move_mouse(self, dx: float, dy: float):
        """Move mouse by delta in pixels."""
        pass

    def __init__(self):
        self._last_cmd: Optional[Command] = None
        self._last_fire_time: float = 0.0
        self._fire_cooldown_sec: float = 0.5

    def set_state(self, cmd: Command):
        """Apply state changes relative to last command to reduce jitter.

        - Holds movement keys while the intent is active
        - Triggers a mouse click when fire is newly activated with cooldown
        """
        now = time()

        # Movement: forward/backward
        if not self._last_cmd or self._last_cmd.forward != cmd.forward:
            if cmd.forward:
                self.press('w')
            else:
                self.release('w')

        if not self._last_cmd or self._last_cmd.backward != cmd.backward:
            if cmd.backward:
                self.press('s')
            else:
                self.release('s')

        # Optional: left/right
        if not self._last_cmd or self._last_cmd.left != cmd.left:
            if cmd.left:
                self.press('a')
            else:
                self.release('a')

        if not self._last_cmd or self._last_cmd.right != cmd.right:
            if cmd.right:
                self.press('d')
            else:
                self.release('d')

        # Brake just releases movement keys (optional mapping)
        if cmd.brake:
            self.release('w')
            self.release('s')
            self.release('a')
            self.release('d')

        # Fire: click with cooldown on rising edge
        if cmd.fire and (not self._last_cmd or not self._last_cmd.fire):
            if now - self._last_fire_time >= self._fire_cooldown_sec:
                self.click_mouse('left')
                self._last_fire_time = now

        # Mouse movement: apply deltas each frame
        if abs(cmd.mouse_dx) > 0.01 or abs(cmd.mouse_dy) > 0.01:
            self.move_mouse(cmd.mouse_dx, cmd.mouse_dy)

        self._last_cmd = cmd