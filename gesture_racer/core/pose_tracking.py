import cv2
import mediapipe as mp
from typing import Dict

from gesture_racer.utils.types import PoseData, PosePoint


class PoseTracker:
    """Wraps MediaPipe Pose to return normalized body keypoints with pixel coordinates."""

    def __init__(self,
                 model_complexity: int = 1,
                 min_detection_confidence: float = 0.6,
                 min_tracking_confidence: float = 0.6):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            enable_segmentation=False,
        )

    def detect(self, bgr_frame) -> PoseData:
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        h, w = bgr_frame.shape[:2]

        points: Dict[str, PosePoint] = {}
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            def add_point(name, idx):
                landmark = lm[idx]
                points[name] = PosePoint(
                    name=name,
                    x=int(landmark.x * w),
                    y=int(landmark.y * h),
                    z=float(landmark.z),
                    visibility=float(landmark.visibility),
                )

            # Key points: shoulders, elbows, wrists, hips, nose
            add_point('left_shoulder', self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            add_point('right_shoulder', self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            add_point('left_elbow', self.mp_pose.PoseLandmark.LEFT_ELBOW)
            add_point('right_elbow', self.mp_pose.PoseLandmark.RIGHT_ELBOW)
            add_point('left_wrist', self.mp_pose.PoseLandmark.LEFT_WRIST)
            add_point('right_wrist', self.mp_pose.PoseLandmark.RIGHT_WRIST)
            add_point('left_hip', self.mp_pose.PoseLandmark.LEFT_HIP)
            add_point('right_hip', self.mp_pose.PoseLandmark.RIGHT_HIP)
            add_point('nose', self.mp_pose.PoseLandmark.NOSE)

        return PoseData(width=w, height=h, points=points)

    def close(self):
        self.pose.close()