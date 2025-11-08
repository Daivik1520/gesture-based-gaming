import cv2
from gesture_racer.core.camera import Camera
from gesture_racer.core.pose_tracking import PoseTracker
from gesture_racer.gestures.gun_pose import GunPoseStrategy
from gesture_racer.gestures.bend_motion import BendMotionStrategy
from gesture_racer.gestures.composite import CompositeStrategy
from gesture_racer.gestures.hand_pan import HandPanStrategy
from gesture_racer.gestures.hand_turn import HandTurnStrategy
from gesture_racer.gestures.panic import PanicGestureStrategy
from gesture_racer.input.pynput_backend import PynputInput
from gesture_racer.overlay.visualization import draw_pose


def main():
    cam = Camera()
    if not cam.open():
        print('Error: Could not open camera.')
        return

    tracker = PoseTracker(model_complexity=1)
    input_backend = PynputInput()

    # Combine strategies: bend motion (forward/back) + gun pose (fire)
    strategy = CompositeStrategy([
        BendMotionStrategy(lean_threshold=0.10),
        GunPoseStrategy(elbow_bent_threshold_deg=70.0, wrist_distance_px=120),
        HandTurnStrategy(dead_zone_px=40, invert_x=False, hysteresis_px=20),
        PanicGestureStrategy(duration_sec=0.8),
        HandPanStrategy(sensitivity=0.6, dead_zone_px=25, max_px_per_frame=30.0, invert_y=False,
                        use_velocity=False, ema_alpha=0.35, neutral_center=True),
    ])

    try:
        while True:
            ok, frame = cam.read()
            if not ok:
                continue

            flipped = cv2.flip(frame, 1)
            pose = tracker.detect(flipped)
            cmd = strategy.evaluate(pose)

            # Apply input state changes
            input_backend.set_state(cmd)

            # Visualize
            draw_pose(flipped, pose)
            status = []
            if cmd.forward: status.append('Forward')
            if cmd.backward: status.append('Backward')
            if cmd.left: status.append('Left')
            if cmd.right: status.append('Right')
            if cmd.brake: status.append('Brake')
            if cmd.fire: status.append('Fire')
            if abs(cmd.mouse_dx) > 0.01 or abs(cmd.mouse_dy) > 0.01:
                status.append(f'Pan dx={cmd.mouse_dx:.1f}, dy={cmd.mouse_dy:.1f}')
            cv2.putText(flipped, ' | '.join(status) if status else 'Idle', (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.putText(flipped, "Press 'q' to quit | 'c' to calibrate", (20, pose.height - 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('Gesture Racer - Body Control', flipped)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                # Calibrate neutral center using current wrist avg
                pose_points = pose.points
                lw = pose_points.get('left_wrist')
                rw = pose_points.get('right_wrist')
                xs, ys = [], []
                if lw:
                    xs.append(lw.x)
                    ys.append(lw.y)
                if rw:
                    xs.append(rw.x)
                    ys.append(rw.y)
                if xs and ys:
                    neutral_x = sum(xs) / len(xs)
                    neutral_y = sum(ys) / len(ys)
                    # Update hand pan neutral
                    for s in strategy.strategies:
                        if isinstance(s, HandPanStrategy):
                            s._neutral_x = neutral_x
                            s._neutral_y = neutral_y
                    cv2.putText(flipped, 'Calibrated', (20, 90), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.imshow('Gesture Racer - Body Control', flipped)

    finally:
        tracker.close()
        cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()