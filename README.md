# Gesture-Based Gaming: Gesture Racer

Modern, modular, and extensible gesture control for racing and action games using MediaPipe Pose and OpenCV.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](#) [![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)](#) [![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-orange)](#)

> Tip: This project is designed with a modular architecture so you can add, remove, or swap out features (gestures, input backends, overlays) with minimal changes.

---


## Key Features

- Hands-free control using body pose and hand positions
- Modular gesture strategies you can mix and match
- Composite strategy merges multiple gestures into a single command stream
- Pluggable input backends (keyboard/mouse via pynput by default)
- Lightweight OpenCV visualization overlay for debugging
- Simple EMA filters for smooth mouse motion
- Cross-platform camera access via OpenCV

---

## Quick Start

1) Install dependencies

```
pip install -r requirements.txt
```

Requirements:
- opencv-python
- mediapipe

2) Run the main app

```
python app.py
```

3) Controls in runtime
- Press `q` to quit
- Press `c` to calibrate neutral center for HandPan (uses current wrist average)

System notes
- Ensure your webcam is connected and accessible
- Good lighting improves pose landmark detection

---

## How It Works (High-Level)

The pipeline processes each frame from your camera:

1. Camera captures frames (OpenCV)
2. PoseTracker runs MediaPipe Pose to extract key landmarks
3. Gesture strategies evaluate landmarks and return a high-level `Command`
4. CompositeStrategy merges multiple strategy outputs
5. Input backend converts `Command` into keyboard/mouse events
6. Overlay draws pose and status for live debugging

```mermaid
flowchart LR
    A[Camera] --> B[PoseTracker]
    B --> C{Gesture Strategies}
    C -->|BendMotion| D1[Cmd]
    C -->|GunPose| D2[Cmd]
    C -->|HandTurn| D3[Cmd]
    C -->|HandPan| D4[Cmd]
    C -->|PanicGesture| D5[Cmd]
    D1 & D2 & D3 & D4 & D5 --> E[CompositeStrategy]
    E --> F[KeyboardMouse Input (pynput)]
    B --> G[Overlay Visualization]
```

---

## Project Structure

```
gesture-based-gaming/
├── app.py                          # Main entry: configures camera, tracker, strategies, input, overlay
├── gesture_racer/
│   ├── core/
│   │   ├── camera.py               # OpenCV camera wrapper
│   │   └── pose_tracking.py        # MediaPipe Pose wrapper returning PoseData
│   ├── gestures/
│   │   ├── base.py                 # GestureStrategy interface (evaluate -> Command)
│   │   ├── bend_motion.py          # Torso lean -> forward/back
│   │   ├── gun_pose.py             # Gun pose -> fire click
│   │   ├── hand_turn.py            # Average wrist X -> left/right booleans with hysteresis
│   │   ├── hand_pan.py             # Average wrist offsets -> mouse pan dx/dy (EMA smoothing)
│   │   ├── panic.py                # Wrists above head (sustained) -> brake & zero mouse
│   │   ├── shoulder_pan.py         # Shoulder depth delta -> mouse pan (optional alt)
│   │   └── composite.py            # Merge multiple strategies
│   ├── input/
│   │   ├── base.py                 # KeyboardMouseInput abstract backend & state diffing
│   │   └── pynput_backend.py       # Concrete backend using pynput for keys/mouse
│   ├── overlay/
│   │   └── visualization.py        # Minimal OpenCV overlay for landmark and status
│   └── utils/
│       ├── filters.py              # EMA smoothing filter
│       └── types.py                # Command, PoseData, PosePoint dataclasses
├── key_input.py                     # Legacy/simple hand-only steering example
├── steering.py                      # Experimental steering wheel gesture demo
├── requirements.txt                 # Dependencies
└── LICENSE                          # MIT license
```

---

## Usage Details

- app.py configures a CompositeStrategy combining:
  - BendMotionStrategy(lean_threshold=0.10) -> forward/back
  - GunPoseStrategy(elbow_bent_threshold_deg=70, wrist_distance_px=120) -> fire
  - HandTurnStrategy(dead_zone_px=40, invert_x=False, hysteresis_px=20) -> left/right
  - PanicGestureStrategy(duration_sec=0.8) -> brake & zero mouse
  - HandPanStrategy(sensitivity=0.6, dead_zone_px=25, max_px_per_frame=30, invert_y=False,
    use_velocity=False, ema_alpha=0.35, neutral_center=True) -> mouse dx/dy

- Pynput backend maps commands to:
  - forward/backward -> W/S
  - left/right -> A/D
  - fire -> left mouse click with 0.5s cooldown
  - mouse movement -> per-frame delta

---

## Gesture Strategies (with visuals)

Each strategy implements `GestureStrategy.evaluate(pose: PoseData) -> Command` and is swappable.

1) Bend Motion
   - Detects torso lean using shoulder vs hip depth (z) to decide forward/back
   - Config: `lean_threshold` (default 0.10)

2) Gun Pose
   - Both elbows bent under threshold and wrists close together -> fire
   - Config: `elbow_bent_threshold_deg`, `wrist_distance_px`
 
3) Hand Turn
   - Average wrist X vs center with dead-zone and hysteresis -> left/right booleans
   - Config: `dead_zone_px`, `invert_x`, `hysteresis_px`
 

4) Hand Pan
   - Average wrist offsets map to mouse dx/dy, EMA smoothing, clamped max per frame
   - Config: `sensitivity`, `dead_zone_px`, `max_px_per_frame`, `invert_y`, `use_velocity`, `ema_alpha`, `neutral_center`
   - Calibrate neutral by pressing `c` in app


5) Panic Gesture
   - Hold both wrists above nose for sustained `duration_sec` -> brake and zero mouse
   - Config: `duration_sec`


Optional: Shoulder Pan
   - Use shoulder depth difference to pan horizontally
   - Config: `z_sensitivity_px_per_unit`, `dead_zone_z`, `max_px_per_frame`

---

## Modular Design and Extension Points

This project is intentionally modular to make adding/removing features easy:

- Gesture module
  - Create a new file in `gesture_racer/gestures/` implementing `GestureStrategy`
  - Return a `Command` with any fields you need (forward/backward/left/right/brake/fire/mouse_dx/mouse_dy)
  - Add your strategy to `CompositeStrategy([...])` in `app.py`

- Input backend
  - Implement `KeyboardMouseInput` in `gesture_racer/input/base.py`
  - Swap `PynputInput` in `app.py` for your custom backend (e.g., game-specific API)

- Overlay
  - Update `gesture_racer/overlay/visualization.py` or add a new overlay

- Tracking
  - Replace `PoseTracker` with alternative detection or parameters

Because strategies are independent and composed, you can quickly swap features on/off.

---

## Configuration Tips

- Performance
  - Lower camera resolution in `Camera(width, height)` for faster processing
  - Reduce `model_complexity` in `PoseTracker` for speed on low-end devices

- Stability
  - Tune `dead_zone_px` and `hysteresis_px` in `HandTurn` to reduce flicker
  - Increase `ema_alpha` in `HandPan` for snappier or smoother feel

- Feel
  - Flip `invert_y` in `HandPan` to match your preference
  - Use `use_velocity=True` for velocity-based panning

---

## Recording and Adding GIFs

1) Use any screen recorder to capture gameplay (OBS, QuickTime, etc.)
2) Export short clips (3–8s) and convert to GIF (e.g., `ffmpeg` or an online tool)
3) Save files in `docs/media/` using names listed in the Demo section
4) Commit and push; GitHub will render them automatically in this README

Example ffmpeg command:

```
ffmpeg -i clip.mp4 -vf "fps=12,scale=960:-1:flags=lanczos" -loop 0 docs/media/gesture-hand-pan.gif
```

---

## Troubleshooting

- No camera detected
  - Check device index in `Camera(device_index=0)`

- Jittery mouse movement
  - Increase `dead_zone_px` and adjust `ema_alpha` in HandPan

- False fire events
  - Raise `elbow_bent_threshold_deg` or lower `wrist_distance_px`

- Keys not registering
  - Some games block synthetic inputs; try running as admin or use a game-specific API backend

---

## FAQ

- Can I replace MediaPipe Pose?
  - Yes. Create a new tracker module returning `PoseData` with the same semantic points and swap it in `app.py`.

- How do I disable a gesture?
  - Remove it from the `CompositeStrategy([...])` list in `app.py`.

- Does it support gamepads?
  - Out of scope by default, but you can build a new input backend that emits controller events.

---

## Roadmap

- Config file for per-game mappings
- Gesture recording and unit tests
- Alternate backends (DirectInput, XInput)
- ML-based gesture classification add-ons

---

## License

Licensed under the MIT License. See [LICENSE](LICENSE).

Copyright (c) 2025 DAIVIK REDDY

---

## Acknowledgments

- MediaPipe Pose by Google
- OpenCV community
