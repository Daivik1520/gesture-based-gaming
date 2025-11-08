from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Command:
    """Represents high-level control intents.

    - forward/backward: movement intents
    - left/right: optional turning intents
    - brake: stop intent
    - fire: trigger a firing action (mouse click)
    """
    forward: bool = False
    backward: bool = False
    left: bool = False
    right: bool = False
    brake: bool = False
    fire: bool = False
    # Mouse movement deltas (pixels per frame)
    mouse_dx: float = 0.0
    mouse_dy: float = 0.0


@dataclass
class PosePoint:
    name: str
    x: int
    y: int
    z: float
    visibility: float


@dataclass
class PoseData:
    width: int
    height: int
    points: Dict[str, PosePoint]