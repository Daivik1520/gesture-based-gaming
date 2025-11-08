import cv2
from gesture_racer.utils.types import PoseData


def draw_pose(frame, pose: PoseData):
    """Draw key pose points and helpful overlays."""
    h, w = pose.height, pose.width
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Draw key points
    for name in ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                 'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'nose']:
        p = pose.points.get(name)
        if p and p.visibility > 0.5:
            color = (0, 255, 255)
            cv2.circle(frame, (p.x, p.y), 6, color, -1)
            cv2.putText(frame, name, (p.x + 5, p.y - 5), font, 0.4, color, 1, cv2.LINE_AA)

    # Center text area
    cv2.putText(frame, 'Gesture Racer Body Mode', (20, 30), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)