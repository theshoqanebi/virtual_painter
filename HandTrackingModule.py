import os
import time

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "hand_landmarker.task")

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


class HandDetector:
    def __init__(self, mode=False, max_hands=2, model_complexity=1,
                 detection_con=0.5, track_con=0.5, model_path=MODEL_PATH):
        # model_complexity kept for backward compatibility (unused by Tasks API)
        self.mode = mode
        self.maxHands = max_hands
        self.detectionCon = detection_con
        self.trackCon = track_con
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=track_con,
            min_tracking_confidence=track_con,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.tipIds = [4, 8, 12, 16, 20]
        self.lmList = []
        self.results = None
        self._lastTs = 0

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        ts = int(time.monotonic() * 1000)
        if ts <= self._lastTs:  # timestamps must strictly increase
            ts = self._lastTs + 1
        self._lastTs = ts
        self.results = self.landmarker.detect_for_video(mp_image, ts)

        if draw and self.results.hand_landmarks:
            h, w, _ = img.shape
            for hand in self.results.hand_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
                for a, b in HAND_CONNECTIONS:
                    cv2.line(img, pts[a], pts[b], (0, 255, 0), 2)
                for p in pts:
                    cv2.circle(img, p, 4, (0, 0, 255), cv2.FILLED)

        return img

    def findPosition(self, img, handNum=0, draw=True):
        self.lmList = []

        if self.results and self.results.hand_landmarks and len(self.results.hand_landmarks) > handNum:
            myHand = self.results.hand_landmarks[handNum]
            for id, lm in enumerate(myHand):
                # print(id, lm);
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                #print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (213, 123, 23), cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        fingers = []

        #Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        #fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)

    detector = HandDetector()
    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        lmList = detector.findPosition(img)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        if(len(lmList) != 0):
            print(lmList[12])
        cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 3,(200,127, 65), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()
