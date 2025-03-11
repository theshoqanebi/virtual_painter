# Virtual Painter

**Draw in the air with your hand.** A webcam-based painting app that tracks your hand with MediaPipe and turns finger gestures into brush strokes and shapes.

> Created as an assignment solution for Computer Engineering at the University of Basrah.

---

## Features

- Freehand drawing with your index finger
- Shape tools: ellipse, circle, rectangle and square
- Four colors: red, yellow, purple and black (black works as an eraser)
- One-gesture canvas clear with the Clean button
- Live hand tracking overlaid on the camera feed

## Gestures

| Gesture                  | Action                                     |
| ------------------------ | ------------------------------------------ |
| Index finger up          | Draw with the current color                |
| Index + middle finger up | Selection mode: point at a toolbar item    |
| Shape tool selected      | Raise index to set a corner, then raise both fingers to place the shape |

## Getting Started

Requirements: Python 3.10+ and a webcam.

```
pip install -r requirements.txt
python VirtualPainter.py
```

## Project Structure

```
VirtualPainter.py        Application window, toolbar and drawing logic
HandTrackingModule.py    MediaPipe hand detector wrapper
images/                  Toolbar images and app icon
requirements.txt         Python dependencies
```
