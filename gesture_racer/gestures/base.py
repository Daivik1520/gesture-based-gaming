from abc import ABC, abstractmethod
from gesture_racer.utils.types import PoseData, Command


class GestureStrategy(ABC):
    @abstractmethod
    def evaluate(self, pose: PoseData) -> Command:
        """Return a Command based on the incoming pose data."""
        pass