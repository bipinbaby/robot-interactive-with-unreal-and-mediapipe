# Robot Arm MediaPipe Controller

A real-time hand tracking system that uses MediaPipe to detect hand gestures and finger movements, sending data via OSC to control a robot arm rig in Unreal Engine 5.

---

## Overview

This project uses a webcam to track hand landmarks using Google's MediaPipe Hand Landmarker. The tracking data is sent as OSC messages to Unreal Engine, where it drives a Control Rig on a robot arm model in real time. Gesture controls include pinch-to-zoom and full finger rotation data.

---

## Requirements

### Python
- Python 3.11 (MediaPipe does not support Python 3.12+)
- mediapipe 0.10.32+
- opencv-python
- python-osc
- numpy

Install all dependencies with:
```bash
py -3.11 -m pip install mediapipe opencv-python python-osc numpy
```

### Unreal Engine
- Unreal Engine 5
- OSC Plugin (built in, enable via Edit → Plugins → OSC)
- Control Rig Plugin (built in, enable via Edit → Plugins → Control Rig)

---

## Project Structure

```
robot-arm-mediapipe/
│
├── opencv_hand.py          # Hand tracking with finger skeleton drawing
├── tdcv.py                 # Hand tracking with OSC output to Unreal/TouchDesigner
├── hand_landmarker.task    # MediaPipe hand model (download separately)
└── README.md
```

> **Note:** The `.task` model file is not included in this repository due to file size. Download it from the link in the Setup section below.

---

## Setup

### Step 1 — Download the Hand Landmarker Model
Download the model file and place it in the same folder as your Python scripts:
```
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

### Step 2 — Run the Python Script
```bash
py -3.11 tdcv.py
```

### Step 3 — Set Up Unreal Engine
1. Enable the **OSC Plugin** via Edit → Plugins
2. Open your **Level Blueprint**
3. On **Event BeginPlay** create an OSC Server:
   - IP Address: `127.0.0.1`
   - Port: `7000`
4. Call **Start Listening** on the server
5. Bind **On OSC Message Received** to your handler function

### Step 4 — Run in the Correct Order
1. Press **Play** in Unreal Engine first
2. Then run the Python script

---

## How It Works

### Hand Tracking
MediaPipe detects 21 landmarks per hand. Each landmark has a normalised x and y coordinate between 0 and 1. The script draws a full hand skeleton on the webcam feed and sends all landmark positions via OSC.

### Left and Right Hand Detection
MediaPipe automatically identifies which hand is which via `result.handedness`. Because the webcam frame is flipped to act as a mirror, the left/right labels are swapped in the script to match what appears on screen.

### OSC Message Format
All values are normalised between 0.0 and 1.0.

| OSC Address | Description |
|-------------|-------------|
| `/Right/wrist/x` | Right wrist horizontal position |
| `/Right/wrist/y` | Right wrist vertical position |
| `/Right/index_tip/x` | Right index fingertip horizontal |
| `/Right/index_tip/y` | Right index fingertip vertical |
| `/Left/wrist/x` | Left wrist horizontal position |
| `/Left/wrist/y` | Left wrist vertical position |
| `/Right/zoom` | Cumulative pinch zoom value |
| `/Left/zoom` | Cumulative pinch zoom value |
| `/Right/rotation` | Overall hand rotation in degrees |
| `/Right/index/angle` | Index finger angle in degrees |
| `/Right/middle/angle` | Middle finger angle in degrees |
| `/Right/ring/angle` | Ring finger angle in degrees |
| `/Right/pinky/angle` | Pinky finger angle in degrees |

### Zoom Gesture
The zoom gesture is cumulative — each pinch adds to the total zoom level rather than the zoom being tied directly to the finger distance. This means you can pinch multiple times to keep zooming, just like a touchscreen. The zoom value is clamped between 0.1 and 10.0.

To trigger a pinch, bring your **thumb tip** and **index finger tip** within a distance of 0.05 (normalised units).

### Rotation Data
Finger and hand rotation angles are calculated using `numpy.arctan2` on the difference in x and y between two landmarks. Angles are output in degrees ranging from -180 to 180.

### Unreal Engine Control Rig
In Unreal, OSC values are received in the Level Blueprint and routed to exposed input variables on the Control Rig asset. The Control Rig Forwards Solve graph reads these variables and applies them to the robot arm controls. Values are remapped from 0–1 to the joint's rotation range using **Map Range Clamped** nodes, and smoothed each frame using **Lerp** to avoid snapping.

---

## Hand Landmark Reference

| Index | Landmark |
|-------|----------|
| 0 | Wrist |
| 1–4 | Thumb (base to tip) |
| 5–8 | Index finger (base to tip) |
| 9–12 | Middle finger (base to tip) |
| 13–16 | Ring finger (base to tip) |
| 17–20 | Pinky (base to tip) |

---

## Known Issues

- MediaPipe only supports Python 3.8 to 3.11. Running on Python 3.12 or above will cause an import error.
- The OSC server in Unreal must be started before running the Python script or messages will be lost.
- The hand landmarker model file must be in the same directory as the Python script or it will not load.
- On Windows, if OSC data is not arriving in Unreal, check that Windows Firewall is not blocking local UDP traffic on port 7000.

---

## Useful Links

- [MediaPipe Hand Landmarker Documentation](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
- [MediaPipe All Solutions](https://ai.google.dev/edge/mediapipe/solutions/guide)
- [Unreal Engine OSC Plugin Documentation](https://docs.unrealengine.com/5.0/en-US/osc-plugin-overview-for-unreal-engine/)
- [python-osc Documentation](https://python-osc.readthedocs.io)# robot-interactive-with-unreal-and-mediapipe
